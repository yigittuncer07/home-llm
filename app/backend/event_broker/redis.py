import json
import redis.asyncio as redis
from constants import REDIS_URL, TASK_QUEUE_NAME, CHAT_STREAM_CHANNEL_PREFIX
from core.logger import logger

# Global client using a connection pool automatically
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def enqueue_task(chat_id: int, user_id: int, message_id: int) -> None:
    task_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message_id": message_id
    }
    await redis_client.rpush(TASK_QUEUE_NAME, json.dumps(task_data))
    
async def dequeue_task(timeout: int = 2) -> dict | None:
    task_json = await redis_client.blpop(TASK_QUEUE_NAME, timeout=timeout) # blocks until a task is available
    if task_json:
        task_data = task_json[1]  # blpop returns a tuple (queue_name, task_data)
        return json.loads(task_data)
    return None
    
async def publish_stream_event(chat_id: int, token: str, is_finished: bool = False) -> None:
    channel = f"{CHAT_STREAM_CHANNEL_PREFIX}:{chat_id}"
    event = {
        "token": token,
        "is_finished": is_finished
    }
    await redis_client.publish(channel, json.dumps(event))
    
async def get_chat_subscriber(chat_id: int):
    """returns a Redis pubsub subscriber for the given chat_id"""
    pubsub = redis_client.pubsub()
    channel = f"{CHAT_STREAM_CHANNEL_PREFIX}:{chat_id}"
    return pubsub, channel