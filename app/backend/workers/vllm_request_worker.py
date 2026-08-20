#backend/workers/vllm_request_worker.py
import asyncio
import json

import httpx
from repository.user_config import UserConfigRepository
from database import SessionLocal  
from models.message import Message
from repository.message import MessageRepository
from event_broker.redis import dequeue_task, publish_stream_event, redis_client
from config import settings
from core.logger import logger
from core.exceptions import LLMAPIError, LLMConnectionError, AppException

DLQ_NAME = f"{settings.task_queue_name}_dlq"

async def process_task(task_data: dict):
    chat_id = task_data["chat_id"]
    user_id = task_data["user_id"]
    original_message_id = task_data["message_id"]

    async with SessionLocal() as session:
        message_repo = MessageRepository(session)
        user_config_repo = UserConfigRepository(session)

        history = await message_repo.get_by_chat_id(chat_id)
        user_config = await user_config_repo.get_by_user_id(user_id)

        dynamic_system_prompt = SYSTEM_PROMPT
        if user_config and user_config.personalized_prompt:
            dynamic_system_prompt += f"\n\nUser Instructions:\n{user_config.personalized_prompt}"

        messages_payload = [{"role": "system", "content": dynamic_system_prompt}]
        for m in history:
            messages_payload.append({"role": m.role, "content": m.content})

        requested_model = history[-1].model

    full_response = ""
    token_count = 0
    
    # truncate messages if they exceed the model's token limit
    logger.info(f"Truncating messages for chat {chat_id} to fit model {requested_model}'s token limit. Before truncation, total messages: {len(messages_payload)}")
    messages_payload = await truncate_messages(messages_payload, requested_model, chat_id)
    logger.info(f"Truncated messages for chat {chat_id}. Total messages after truncation: {len(messages_payload)}")

    payload = {
        "model": requested_model,
        "messages": messages_payload,
        "stream": True,
        "max_tokens": MAX_LLM_TOKENS
    }

    # sse streaming loop to redis
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", LLM_API_URL, json=payload) as response:

                if response.status_code >= 400:
                    await response.aread()
                    raise LLMAPIError(
                        chat_id=chat_id,
                        api_status_code=response.status_code,
                        api_error_body=response.text,
                    )

                async for line in response.aiter_lines():
                    if line.strip() == "data: [DONE]":
                        break

                    content = parse_sse_line(line, chat_id)
                    if not content:
                        continue

                    full_response += content
                    token_count += 1
                    await publish_stream_event(chat_id=chat_id, token=content, is_finished=False)

    except httpx.RequestError as e:
        raise LLMConnectionError(chat_id=chat_id, original_error=e) from e

    # 3. Finalize: Save assistant message to Database
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

    # 4. Publish completion event
    await publish_stream_event(chat_id=chat_id, token="", is_finished=True)
    logger.info(f"Finished processing and saved assistant message for chat {chat_id}")


def parse_sse_line(line: str, chat_id: int) -> str | None:
    """Extract content from one SSE line. Returns None if there's nothing to emit."""
    if not line.startswith("data: "):
        return None

    data = line[len("data: "):]
    if data == "[DONE]":
        return None

    try:
        chunk = json.loads(data)
        return chunk["choices"][0].get("delta", {}).get("content", "")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for chat {chat_id}. Raw data: '{data}'. Error: {e}")
        return None
    
async def get_token_count(messages: list[dict], model: str, chat_id: int) -> tuple[int, int]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKENIZE_URL,
            json={"model": model, "messages": messages}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("count"), data.get("max_model_len")
        else:
            raise LLMConnectionError(
                chat_id=chat_id, 
                original_error=Exception(f"Tokenize request failed with status {response.status_code}")
            )

async def truncate_messages(messages: list[dict], model: str, chat_id: int) -> list[dict]:
    while len(messages) > 1:
        total_tokens, max_model_len = await get_token_count(messages, model, chat_id)
        
        if total_tokens <= (max_model_len - MAX_LLM_TOKENS):
            break
            
        # Drop the oldest user/assistant pair (indices 1 and 2) to preserve chat structure.
        # If there are at least 3 items (system + user + assistant):
        if len(messages) >= 3:
            messages.pop(1) # Drop oldest user message
            messages.pop(1) # Drop corresponding assistant message (which shifted to index 1)
        else:
            # Fallback if only 1 message remains after system prompt but it still exceeds limits
            messages.pop(1)
        
    return messages

async def main():
    logger.info("Worker started, waiting for tasks...")
    while True:
        try:
            task = await dequeue_task(timeout=3)

            if task:
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

        except Exception as e:
            logger.error(f"Critical Queue Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker gracefully shutting down.")