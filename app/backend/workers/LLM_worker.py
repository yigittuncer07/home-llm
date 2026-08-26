import asyncio
import json

from database import SessionLocal
from repository.user_config import UserConfigRepository
from repository.user_token_balance import UserTokenBalanceRepository
from repository.message import MessageRepository
from models.message import Message
from event_broker.redis import dequeue_task, publish_stream_event, redis_client
from config import settings
from core.logger import logger
from core.exceptions import AppException, LLMAPIError, LLMConnectionError
from workers.providers.factory import get_provider

DLQ_NAME = f"{settings.task_queue_name}_dlq"
semaphore = asyncio.Semaphore(settings.max_concurrency)
running_tasks = set()


async def _prepare_chat_context(chat_id: int, user_id: int) -> tuple[list[dict], str]:
    """Fetches chat history and formats the system prompt."""
    async with SessionLocal() as session:
        history = await MessageRepository(session).get_by_chat_id(chat_id)
        user_config = await UserConfigRepository(session).get_by_user_id(user_id)

        if not history:
            raise AppException(500, detail=f"Chat history is empty for chat {chat_id}.")

        prompt = settings.system_prompt
        if user_config and user_config.personalized_prompt:
            prompt += f"\n\nUser Instructions:\n{user_config.personalized_prompt}"

        messages = [{"role": "system", "content": prompt}]
        messages.extend([{"role": m.role, "content": m.content} for m in history])
        
        return messages, history[-1].model


async def _stream_llm_with_retries(chat_id: int, requested_model: str, messages: list[dict], model_config: dict) -> tuple[str, int]: # type: ignore
    """Handles API calls, streaming, and retry/backoff logic."""
    provider = get_provider(model_config["provider_type"])
    messages = await provider.truncate_messages(requested_model, messages, model_config)

    for attempt in range(settings.max_retries + 1):
        try:
            full_response, token_count = "", 0
            async for content in provider.stream_response(requested_model, messages, model_config):
                full_response += content
                token_count += 1
                await publish_stream_event(chat_id=chat_id, token=content, is_finished=False)
            return full_response, token_count

        except (LLMAPIError, LLMConnectionError) as e:
            status_code = getattr(e, 'api_status_code', None)
            is_retryable = isinstance(e, LLMConnectionError) or status_code in (429, 503)

            if is_retryable and attempt < settings.max_retries:
                retry_after = getattr(e, 'headers', {}).get("Retry-After")
                wait_time = int(retry_after) if retry_after and str(retry_after).isdigit() else 2 ** attempt
                
                logger.warning(f"Error for chat {chat_id}. Retrying in {wait_time}s... ({attempt + 1}/{settings.max_retries})")
                await asyncio.sleep(wait_time)
            else:
                error_msg = "Rate limit exceeded. Please try again later." if status_code == 429 else "Service unavailable."
                await publish_stream_event(chat_id=chat_id, token=f"\n\n**[System: {error_msg}]**", is_finished=True)
                raise AppException(502, detail=error_msg, log_message=f"Fatal error for chat {chat_id}: {e}")


async def _save_assistant_response(chat_id: int, user_id: int, model: str, content: str, tokens: int):
    """Commits the final response and deducts tokens."""
    async with SessionLocal() as session:
        await MessageRepository(session).add(Message(
            chat_id=chat_id, model=model, tokens=tokens, role="assistant", content=content
        ))
        await UserTokenBalanceRepository(session).decrement_balance(user_id, model, tokens)
        await session.commit()
        
    await publish_stream_event(chat_id=chat_id, token="", is_finished=True)
    logger.info(f"Finished processing and saved assistant message for chat {chat_id}")


async def process_task(task_data: dict):
    chat_id, user_id = task_data["chat_id"], task_data["user_id"]

    messages, requested_model = await _prepare_chat_context(chat_id, user_id)

    raw_model_config = settings.models_config.get(requested_model)
    if not raw_model_config:
        raise AppException(400, detail=f"Model {requested_model} not supported.", log_message=f"Model {requested_model} missing.")
    
    model_config = raw_model_config.copy()
    model_config["chat_id"] = chat_id

    full_response, token_count = await _stream_llm_with_retries(chat_id, requested_model, messages, model_config)
    await _save_assistant_response(chat_id, user_id, requested_model, full_response, token_count)


async def push_to_dlq_safe(task: dict):
    """Fix 2: Guard against Redis failures when pushing to DLQ."""
    try:
        await redis_client.rpush(DLQ_NAME, json.dumps(task))
    except Exception as e:
        logger.critical(f"FATAL: Could not push task {task.get('chat_id')} to DLQ. Error: {e}\nTask Data: {task}")


async def process_and_release(task: dict):
    chat_id = task.get('chat_id')
    logger.info(f"Processing task for chat {chat_id}")
    try:
        await process_task(task)
    except AppException as e:
        logger.error(f"Task failed for chat {chat_id}: {e.log_message}. Moving to DLQ.")
        task.update({"error": e.log_message, "error_code": e.status_code})
        await push_to_dlq_safe(task)
    except Exception as e:
        logger.exception(f"Unexpected error for chat {chat_id}. Moving to DLQ.")
        task["error"] = str(e)
        await push_to_dlq_safe(task)
    finally:
        semaphore.release()


async def main():
    logger.info(f"Worker started with concurrency limit {settings.max_concurrency}, waiting for tasks...")
    while True:
        try:
            await semaphore.acquire()
            task = await dequeue_task(timeout=3)
            if task:
                t = asyncio.create_task(process_and_release(task))
                running_tasks.add(t)
                t.add_done_callback(running_tasks.discard)
            else:
                semaphore.release()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Worker Loop Error: {e}")
            semaphore.release()
            await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = loop.create_task(main())
    
    try:
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Draining in-flight tasks (this may take a moment)...")
        main_task.cancel()
        
        if running_tasks:
            loop.run_until_complete(asyncio.gather(*running_tasks, return_exceptions=True))
            
        logger.info("Worker shutdown complete.")
    finally:
        loop.close()