import os
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.logger import logger

def load_models_config() -> dict:
    # Adjust this path based on where you placed models.yaml relative to config.py
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './models.yaml'))
    
    if not os.path.exists(yaml_path):
        return {}
        
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return data.get("models", {}) if data else {}

class Settings(BaseSettings):
    # loaded automatically from .env
    db_user: str
    db_password: str
    db_name: str
    db_host: str = "localhost"
    db_port: int = 5432
    admin_email: str
    admin_password: str
    
    jwt_key: str
    redis_host: str = "localhost"

    # dynamic Model Configuration loaded from models.yaml
    models_config: dict = Field(default_factory=load_models_config)
    logger.info("Loaded models configuration: %s", models_config)

    # constants
    task_queue_name: str = "task_queue"
    chat_stream_channel_prefix: str = "chat_stream"
    system_prompt: str = (
        "You are a helpful, objective, and highly capable AI assistant. "
        "Provide accurate, clear, and direct answers."
    )

    # max concurrency for processing tasks
    max_concurrency: int = 50
    max_retries: int = 3
    
    # variables
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:6379/0"

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings() # type: ignore