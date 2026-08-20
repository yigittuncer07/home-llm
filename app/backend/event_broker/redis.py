#backend/event_broker/redis.py
import json
import redis.asyncio as redis
from config import settings
from core.logger import logger

# Global client using a connection pool automatically
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def enqueue_task(chat_id: int, user_id: int, message_id: int) -> None:
    task_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message_id": message_id
    }
    await redis_client.rpush(settings.task_queue_name, json.dumps(task_data))
    
async def dequeue_task(timeout: int = 2) -> dict | None:
    task_json = await redis_client.blpop(settings.task_queue_name, timeout=timeout) # blocks until a task is available
    if task_json:
        task_data = task_json[1]  # blpop returns a tuple (queue_name, task_data)
        return json.loads(task_data)
    return None
    
async def publish_stream_event(chat_id: int, token: str, is_finished: bool = False) -> None:
    channel = f"{settings.chat_stream_channel_prefix}:{chat_id}"
    event = {
        "token": token,
        "is_finished": is_finished
    }
    await redis_client.publish(channel, json.dumps(event))
    
async def get_chat_subscriber(chat_id: int) -> tuple[redis.client.PubSub, str]:
    """returns a Redis pubsub subscriber for the given chat_id"""
    pubsub = redis_client.pubsub()
    channel = f"{settings.chat_stream_channel_prefix}:{chat_id}"
    return pubsub, channel