#backend/services/admin.py

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from repository.user import UserRepository
from core.exceptions import UserNotFoundError
from models.user import UserResponse

async def get_all_users_service(session: AsyncSession) -> list[UserResponse]:
    user_repository = UserRepository(session)
    users = await user_repository.get_all()
    logging.info(f"Retrieved {len(users)} users from the database.")
    
    return [UserResponse.model_validate(user) for user in users]

async def delete_user_service(session: AsyncSession, user_id: int) -> UserResponse:
    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)
    
    if not user:
        log_message = f"Attempted to delete non-existent user with id {user_id}."
        logging.warning(log_message)
        raise UserNotFoundError(user_id, log_message=log_message)
    
    await user_repository.delete(user)
    logging.info(f"Deleted user with id {user_id}.")
    
    return UserResponse.model_validate(user)