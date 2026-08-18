import asyncio
import json
from database import SessionLocal  
from models.message import Message
from repository.message import MessageRepository
from event_broker.redis import dequeue_task, publish_stream_event, redis_client
from constants import TASK_QUEUE_NAME
from core.logger import logger


DLQ_NAME = f"{TASK_QUEUE_NAME}_dlq"

async def process_task(task_data: dict):
    # TODO: Tie to actual VLLM
    # TODO: Add error handling and retries for VLLM processing, using priority queues or a dead-letter queue (DLQ) for failed tasks.
    # TODO: Get user personal prefences and inject into prompt.
    # TODO: Get a fixed system prompt from a configuration file
    
    
    chat_id = task_data["chat_id"]
    user_id = task_data["user_id"]
    original_message_id = task_data["message_id"]

    logger.info(f"Processing task for chat {chat_id}, user {user_id}")

    # 1. Simulate LLM initialization/thinking time
    await asyncio.sleep(2)

    # Dummy response data
    dummy_tokens = ["Here ", "is ", "your ", "simulated ", "response ", "from ", "the ", "worker!"]
    full_response = ""

    # 2. Stream tokens via Redis Pub/Sub
    for token in dummy_tokens:
        full_response += token
        await publish_stream_event(chat_id=chat_id, token=token, is_finished=False)
        await asyncio.sleep(0.2)  # Simulate token generation delay

    # 3. Finalize: Save assistant message to Database
    async with SessionLocal() as session:
        message_repo = MessageRepository(session)
        assistant_message = Message(
            chat_id=chat_id,
            model="qwen",
            tokens=len(dummy_tokens),
            role="assistant",
            content=full_response,
            timestamp=None
        )
        await message_repo.add(assistant_message)
        await session.commit() # Commit the transaction
        
    # 4. Publish completion event
    await publish_stream_event(chat_id=chat_id, token="", is_finished=True)
    logger.info(f"Finished processing and saved assistant message for chat {chat_id}")

async def main():
    logger.info("Worker started, waiting for tasks...")
    while True:
        try:
            task = await dequeue_task(timeout=3)  
            
            if task:
                try:
                    await process_task(task)
                except Exception as e:
                    logger.error(f"Task failed for chat {task.get('chat_id')}: {e}. Moving to DLQ.")
                    # Move to Dead Letter Queue with the error message attached
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