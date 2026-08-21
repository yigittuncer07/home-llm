#backend/services/chats.py

import json
import logging # TODO: use the central logger instead

from sqlalchemy.ext.asyncio import AsyncSession

from event_broker.redis import get_chat_subscriber
from models.chat import Chat, ChatDeleteResponse, ChatsResponse, ChatItem
from repository.chat import ChatRepository
from core.exceptions import ChatNotFoundError, PermissionDeniedError

async def get_chats_by_user_id(user_id: str, session: AsyncSession) -> ChatsResponse:
    chat_repository = ChatRepository(session)
    chats = await chat_repository.get_by_user_id(int(user_id))
    logging.info(f"Retrieved {len(chats)} chats for user ID: {user_id}")
    
    return ChatsResponse.model_validate({"chats": chats})

async def add_new_chat(user_id: str, title: str | None, session: AsyncSession) -> ChatItem:
    chat_repository = ChatRepository(session)
    if not title:
        title = "New Chat"
    new_chat = await chat_repository.add(
        Chat(
            user_id=int(user_id),
            title=title
        )
    )
    logging.info(f"Created new chat with ID: {new_chat.chat_id} for user ID: {user_id} with title: {title}")
    return ChatItem.model_validate(new_chat)

async def delete_chat_by_id(chat_id: int, user_id: str, session: AsyncSession) -> ChatDeleteResponse:
    chat_repository = ChatRepository(session)
    chat = await chat_repository.get_by_id(chat_id)
    
    if not chat:
        log_message = f"Chat with ID: {chat_id} not found for deletion."
        logging.warning(log_message)
        raise ChatNotFoundError(chat_id=chat_id, log_message=log_message)
    
    if chat.user_id != int(user_id):
        log_message = f"User ID: {user_id} attempted to delete chat ID: {chat_id} without permission."
        logging.warning(log_message)
        raise PermissionDeniedError(log_message=log_message)
    
    await session.delete(chat)
    await session.commit()
    logging.info(f"Deleted chat with ID: {chat_id} for user ID: {user_id}.")
    
    return ChatDeleteResponse.model_validate({"message": "Chat deleted successfully."})
    
async def update_chat_title(chat_id: int, user_id: str, title: str, session: AsyncSession) -> ChatItem:
    chat_repository = ChatRepository(session)
    chat = await chat_repository.get_by_id(chat_id)

    if not chat:
        log_message = f"Chat with ID: {chat_id} not found for update."
        logging.warning(log_message)
        raise ChatNotFoundError(chat_id=chat_id, log_message=log_message)

    if chat.user_id != int(user_id):
        log_message = f"User ID: {user_id} attempted to update chat ID: {chat_id} without permission."
        logging.warning(log_message)
        raise PermissionDeniedError(log_message=log_message)

    chat.title = title
    await session.commit()
    await session.refresh(chat)
    logging.info(f"Updated chat with ID: {chat_id} for user ID: {user_id} with new title: {title}")

    return ChatItem.model_validate(chat)

async def chat_stream_generator(chat_id: int):
    pubsub, channel = await get_chat_subscriber(chat_id=chat_id)
    await pubsub.subscribe(channel)
    
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data_str = message['data']
                yield f"data: {data_str}\n\n"
                
                data_dict = json.loads(data_str)
                if data_dict.get('is_finished'):
                    break
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()