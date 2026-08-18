from models.chat import Chat
from repository.chat import ChatRepository
from core.exceptions import ChatNotFoundError, PermissionDeniedError
from core.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

async def verify_chat_ownership(chat_id: int, user_id: str, session: AsyncSession) -> Chat:
    chat_repository = ChatRepository(session)
    chat = await chat_repository.get_by_id(chat_id)
    
    if not chat:
        logger.error(f"User {user_id} attempted to access non-existent chat {chat_id}")
        raise ChatNotFoundError(chat_id=chat_id, log_message=f"Chat {chat_id} not found for user {user_id}")
    elif chat.user_id != int(user_id):
        logger.error(f"User {user_id} attempted to access chat {chat_id} they do not own")
        raise PermissionDeniedError(log_message=f"User {user_id} does not have permission to access chat {chat_id}")
        
    return chat