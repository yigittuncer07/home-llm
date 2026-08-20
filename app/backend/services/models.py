#backend/services/models.py

from config import settings
from core.logger import logger

async def get_models_service() -> list[str]:
    """
    Get a list of available models for the authenticated user.
    """
    models = list(settings.models_config.keys())
    logger.info(f"Retrieved {len(models)} available models.")
    return models