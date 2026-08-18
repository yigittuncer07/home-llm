#backend/services/messages.py

from models.message import Message, SendMessageRequest
from sqlalchemy.ext.asyncio import AsyncSession
from repository.message import MessageRepository
from event_broker.redis import enqueue_task
from core.logger import logger
from core.exceptions import InternalServerError

async def enqueue_message(request: SendMessageRequest, user_id: str, chat_id: int, session: AsyncSession):
    message_repository = MessageRepository(session)

    new_message = Message(
        chat_id=chat_id,
        model=request.model,
        tokens=None, # will be set by the worker 
        role="user", 
        content=request.prompt,
        timestamp=None # will be set by the database
    )
    try:
        message = await message_repository.add(new_message)
    except Exception as e:
        logger.error(f"Failed to write to database for chat {chat_id} by user {user_id}: {e}")
        raise InternalServerError(log_message=str(e)) from e
    
    logger.info(f"Enqueued message with ID {message.message_id} for chat {chat_id} by user {user_id}")
    
    try:
        await enqueue_task(
                chat_id=chat_id,
                user_id=int(user_id),
                message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Failed to enqueue task for message ID {message.message_id} in chat {chat_id} by user {user_id}: {e}")
        raise InternalServerError(log_message=str(e)) from e
    
    logger.info(f"Task enqueued for message ID {message.message_id} in chat {chat_id} by user {user_id}")
    
    return "Message enqueued successfully"