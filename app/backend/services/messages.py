#backend/services/messages.py

from repository.chat import ChatRepository
from models.message import Message, SendMessageRequest, ChatHistoryResponse, ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from repository.message import MessageRepository
from event_broker.redis import enqueue_task
from core.logger import logger
from core.exceptions import InternalServerError, ChatNotFoundError, PermissionDeniedError
from core.helpers import ensure_positive_balance, verify_chat_ownership

async def enqueue_message(request: SendMessageRequest, user_id: str, chat_id: int, session: AsyncSession) -> str:
    # verify chat ownership
    await verify_chat_ownership(chat_id, user_id, session)
        
    await ensure_positive_balance(int(user_id), request.model, session)

    message_repository = MessageRepository(session)

    new_message = Message(
        chat_id=chat_id,
        model=request.model,
        tokens=None, # will be set by the worker 
        role="user", 
        content=request.prompt,
        timestamp=None # will be set by the database
    )
    logger.info(f"Enqueuing message for chat {chat_id} by user {user_id} with model {request.model}. Prompt: {request.prompt}")
    try:
        message = await message_repository.add(new_message)
        await session.flush()  # flush to get the message_id before commit
        message_id = message.message_id
        await session.commit() # to prevent race conditions
    except Exception as e:
        logger.error(f"Failed to write to database for chat {chat_id} by user {user_id}: {e}")
        raise InternalServerError(log_message=str(e)) from e
    
    logger.info(f"Enqueued message with ID {message_id} for chat {chat_id} by user {user_id}")
    
    try:
        await enqueue_task(
                chat_id=chat_id,
                user_id=int(user_id),
                message_id=message_id
        )
    except Exception as e:
        logger.error(f"Failed to enqueue task for message ID {message_id} in chat {chat_id} by user {user_id}: {e}")
        raise InternalServerError(log_message=str(e)) from e
    
    logger.info(f"Task enqueued for message ID {message_id} in chat {chat_id} by user {user_id}")
    
    return "Message enqueued successfully"

async def get_chat_history_service(chat_id: int, user_id: str, session: AsyncSession) -> ChatHistoryResponse:
    # verify chat ownership
    await verify_chat_ownership(chat_id, user_id, session)
    
    message_repository = MessageRepository(session)
    
    try:
        messages = await message_repository.get_by_chat_id(chat_id)
    except Exception as e:
        logger.error(f"Failed to retrieve chat history from database for chat {chat_id} by user {user_id}: {e}")
        raise InternalServerError(log_message=str(e)) from e
    
    logger.info(f"Retrieved chat history for chat {chat_id} by user {user_id} with {len(messages)} messages")
    
    return ChatHistoryResponse(chat_id=chat_id, messages=[ChatMessage.model_validate(message) for message in messages])