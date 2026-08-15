#backend/services/chats.py

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import ChatsResponse
from repository.chat import ChatRepository

async def get_chats_by_user_id(user_id: str, session: AsyncSession) -> ChatsResponse:
    chat_repository = ChatRepository(session)
    chats = await chat_repository.get_by_user_id(int(user_id))
    logging.info(f"Retrieved {len(chats)} chats for user ID: {user_id}")
    
    return ChatsResponse.model_validate({"chats": chats})