import os
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.environ['jwt_key']
DATABASE_URL = os.environ['database_url']
REDIS_URL = os.environ['redis_url']
TASK_QUEUE_NAME = os.environ['task_queue_name']
CHAT_STREAM_CHANNEL_PREFIX = os.environ['chat_stream_channel_prefix']
LLM_API_URL = os.environ['llm_api_url']
SYSTEM_PROMPT = os.environ['system_prompt']
MAX_LLM_TOKENS = int(os.environ['max_llm_tokens'])