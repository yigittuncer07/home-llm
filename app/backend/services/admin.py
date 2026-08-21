#backend/services/admin.py

from sqlalchemy.ext.asyncio import AsyncSession
from repository.chat import ChatRepository
from models.chat import ChatDeleteResponse, ChatItem
from core.exceptions import PermissionDeniedError
from auth.security import hash_password
from repository.user import UserRepository, User
from models.user import UserResponse
from core.exceptions import ChatNotFoundError, UserAlreadyExistsError, UserNotFoundError
from repository.user_token_balance import UserTokenBalanceRepository
from models.user_token_balance import TokenBalanceResponse
from core.logger import logger

async def delete_user_service(session: AsyncSession, user_id: int) -> UserResponse:
    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)
    
    if not user:
        log_message = f"Attempted to delete non-existent user with id {user_id}."
        logger.warning(log_message)
        raise UserNotFoundError(user_id, log_message=log_message)
    
    await user_repository.delete(user)
    logger.info(f"Deleted user with id {user_id}.")
    
    return UserResponse.model_validate(user)

async def register_user_service(email: str, password: str, session: AsyncSession) -> UserResponse:
    user_repository = UserRepository(session)
    user = await user_repository.get_by_email(email)
    
    if user:
        raise UserAlreadyExistsError(email, log_message=f"Attempt to register existing user with email: {email} ID: {user.id}")

    user = await user_repository.add(
        User(
            email=email,
            password_hash=hash_password(password)
        )
    )
    logger.info(f"User registered with email: {email} ID: {user.id}")

    return UserResponse.model_validate(user)


async def set_user_tokens_service(user_id: int, model_name: str, balance: int, session: AsyncSession) -> TokenBalanceResponse:
    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)
    
    if not user:
        raise UserNotFoundError(user_id, log_message=f"Cannot set tokens. User {user_id} not found.")

    token_repo = UserTokenBalanceRepository(session)
    record = await token_repo.set_balance(user_id, model_name, balance)
    
    logger.info(f"Set token balance for user {user_id} on model {model_name} to {balance}.")
    
    return TokenBalanceResponse.model_validate(record)

async def get_all_users_service(session: AsyncSession) -> list[UserResponse]:
    user_repository = UserRepository(session)
    users = await user_repository.get_all()
    logger.info(f"Retrieved {len(users)} users from the database.")
    
    return [UserResponse.model_validate(user) for user in users]

async def get_user_details_service(user_id: int, session: AsyncSession) -> UserResponse:
    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)
    
    if not user:
        log_message = f"Attempted to fetch details for non-existent user with id {user_id}."
        logger.warning(log_message)
        raise UserNotFoundError(user_id, log_message=log_message)

    logger.info(f"Retrieved details for user {user_id}.")
    return UserResponse.model_validate(user)

async def delete_chat_by_id(chat_id: int, session: AsyncSession) -> ChatItem:
    chat_repository = ChatRepository(session)
    chat = await chat_repository.get_by_id(chat_id)
    
    if not chat:
        log_message = f"Chat with ID: {chat_id} not found for deletion."
        logger.warning(log_message)
        raise ChatNotFoundError(chat_id=chat_id, log_message=log_message)
    
    await session.delete(chat)
    await session.commit()
    logger.info(f"Deleted chat with ID: {chat_id} for user ID: {chat.user_id}.")
    
    return ChatItem.model_validate(chat)

async def get_user_chats_service(user_id: int, session: AsyncSession) -> list[ChatItem]:
    chat_repository = ChatRepository(session)
    chats = await chat_repository.get_by_user_id(user_id)
    
    logger.info(f"Retrieved {len(chats)} chats for user ID: {user_id}.")
    
    return [ChatItem.model_validate(chat) for chat in chats]