import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # loaded automatically from .env
    db_user: str
    db_password: str
    db_name: str
    db_host: str = "localhost"
    db_port: int = 5432
    
    jwt_key: str
    
    redis_host: str = "localhost"
    llm_api_base: str

    # constants
    task_queue_name: str = "task_queue"
    chat_stream_channel_prefix: str = "chat_stream"
    system_prompt: str = (
        "You are a helpful, objective, and highly capable AI assistant. "
        "Provide accurate, clear, and direct answers."
    )

    # variables
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:6379/0"
        
    @property
    def llm_api_url(self) -> str:
        return f"{self.llm_api_base}/v1/chat/completions"
        
    @property
    def tokenize_url(self) -> str:
        return f"{self.llm_api_base}/tokenize"

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()