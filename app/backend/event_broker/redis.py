import json
import redis.asyncio as redis
from constants import REDIS_URL

# Global client using a connection pool automatically
redis_client = redis.from_url(REDIS_URL, decode_responses=True)