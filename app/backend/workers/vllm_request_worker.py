import asyncio
import json

from repository.user_config import UserConfigRepository
from database import SessionLocal  
from models.message import Message
from repository.message import MessageRepository
from event_broker.redis import dequeue_task, publish_stream_event, redis_client
from config import settings
from core.logger import logger
from core.exceptions import AppException, LLMAPIError, LLMConnectionError
from providers.factory import get_provider

DLQ_NAME = f"{settings.task_queue_name}_dlq"
semaphore = asyncio.Semaphore(settings.max_concurrency)

async def process_task(task_data: dict):
    chat_id = task_data["chat_id"]
    user_id = task_data["user_id"]

    async with SessionLocal() as session:
        message_repo = MessageRepository(session)
        user_config_repo = UserConfigRepository(session)

        history = await message_repo.get_by_chat_id(chat_id)
        user_config = await user_config_repo.get_by_user_id(user_id)

        if not history:
            raise AppException(
                status_code=500, 
                detail=f"Chat history is empty for chat {chat_id}.",
                log_message=f"Chat history is empty for chat {chat_id}."
            )

        dynamic_system_prompt = settings.system_prompt
        if user_config and user_config.personalized_prompt:
            dynamic_system_prompt += f"\n\nUser Instructions:\n{user_config.personalized_prompt}"

        messages_payload = [{"role": "system", "content": dynamic_system_prompt}]
        for m in history:
            messages_payload.append({"role": m.role, "content": m.content})

        requested_model = history[-1].model

    model_config = settings.models_config.get(requested_model)
    if not model_config:
        raise AppException(
            status_code=400,
            detail=f"Model {requested_model} is not supported or not configured.",
            log_message=f"Model {requested_model} is not supported or not configured."
        )

    model_config["chat_id"] = chat_id
    provider_type = model_config["provider_type"]
    provider = get_provider(provider_type)

    logger.info(f"Truncating messages for chat {chat_id}.")
    messages_payload = await provider.truncate_messages(requested_model, messages_payload, model_config)

    full_response = ""
    token_count = 0
    success = False

    # Retry loop with backoff
    for attempt in range(settings.max_retries + 1):
        try:
            full_response = ""
            token_count = 0

            async for content in provider.stream_response(requested_model, messages_payload, model_config):
                full_response += content
                token_count += 1
                await publish_stream_event(chat_id=chat_id, token=content, is_finished=False)
            
            success = True
            break

        except (LLMAPIError, LLMConnectionError) as e:
            status_code = getattr(e, 'api_status_code', None)
            is_retryable = isinstance(e, LLMConnectionError) or status_code in (429, 503)

            if is_retryable and attempt < settings.max_retries:
                # Use Retry-After header if available, otherwise exponential backoff
                headers = getattr(e, 'headers', {})
                retry_after = headers.get("Retry-After")
                
                if retry_after and str(retry_after).isdigit():
                    wait_time = int(retry_after)
                else:
                    wait_time = 2 ** attempt
                    
                logger.warning(f"Provider error for chat {chat_id} (Code: {status_code}). Retrying in {wait_time}s... (Attempt {attempt + 1}/{settings.max_retries})")
                await asyncio.sleep(wait_time)
            else:
                error_msg = "Rate limit exceeded. Please try again later." if status_code == 429 else "Service unavailable or connection failed."
                # Publish failure message directly to the user's stream
                await publish_stream_event(chat_id=chat_id, token=f"\n\n**[System: {error_msg}]**", is_finished=True)
                
                raise AppException(
                    status_code=502,
                    detail=error_msg,
                    log_message=f"Max retries exceeded or fatal error for chat {chat_id}: {e}"
                )

    if success:
        async with SessionLocal() as session:
            message_repo = MessageRepository(session)
            assistant_message = Message(
                chat_id=chat_id,
                model=requested_model,
                tokens=token_count,
                role="assistant",
                content=full_response,
                timestamp=None
            )
            await message_repo.add(assistant_message)
            await session.commit()

        await publish_stream_event(chat_id=chat_id, token="", is_finished=True)
        logger.info(f"Finished processing and saved assistant message for chat {chat_id}")

async def process_and_release(task: dict):
    try:
        await process_task(task)
    except AppException as e:
        logger.error(f"Task failed for chat {task.get('chat_id')}: {e.log_message}. Moving to DLQ.")
        task["error"] = e.log_message
        task["error_code"] = e.status_code
        await redis_client.rpush(DLQ_NAME, json.dumps(task))
    except Exception as e:
        logger.exception(f"Unexpected error for chat {task.get('chat_id')}. Moving to DLQ.")
        task["error"] = str(e)
        await redis_client.rpush(DLQ_NAME, json.dumps(task))
    finally:
        semaphore.release()

async def main():
    logger.info(f"Worker started with concurrency limit {settings.max_concurrency}, waiting for tasks...")
    while True:
        try:
            await semaphore.acquire()
            try:
                task = await dequeue_task(timeout=3)
            except Exception as e:
                semaphore.release()
                logger.error(f"Critical Queue Error during dequeue: {e}")
                await asyncio.sleep(5)
                continue

            if task:
                asyncio.create_task(process_and_release(task))
            else:
                semaphore.release()

        except Exception as e:
            logger.error(f"Critical Worker Loop Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker gracefully shutting down.")