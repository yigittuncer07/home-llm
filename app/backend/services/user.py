#backend/services/user.py
import logging
from models.user_config import UserConfigResponse, UserConfig
from repository.user_config import UserConfigRepository


async def get_user_config_service(user_id: str, session) -> UserConfigResponse:
    config_repository = UserConfigRepository(session)
    user_config = await config_repository.get_by_user_id(int(user_id))
    if not user_config:
        logging.info(f"No user config found for user_id: {user_id}. Returning default config.")
        return UserConfigResponse(personalized_prompt="")
    return UserConfigResponse.model_validate(user_config)

async def update_user_config_service(user_id: str, personalized_prompt: str, session) -> UserConfigResponse:
    config_repository = UserConfigRepository(session)
    user_config = await config_repository.get_by_user_id(int(user_id))
    
    if not user_config:
        logging.info(f"No user config found for user_id: {user_id}. Creating new config.")
    else:
        logging.info(f"Updating user config for user_id: {user_id}.")
        
    user_config = await config_repository.upsert(UserConfig(user_id=int(user_id), personalized_prompt=personalized_prompt))
    
    return UserConfigResponse.model_validate(user_config)
