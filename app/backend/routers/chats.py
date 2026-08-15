#backend/routers/chats.py
from fastapi import APIRouter, Depends
from auth.dependencies import require_auth_token
from services.chats import get_chats_by_user_id, add_new_chat, delete_chat_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.chat import ChatsResponse, ChatDeleteResponse

router = APIRouter()

@router.get("", response_model=ChatsResponse)
async def get_chats(
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db)
) -> ChatsResponse:
    chats = await get_chats_by_user_id(user_id=user_id, session=session)
    return chats

@router.post("", response_model=ChatsResponse)
async def create_chat(
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db)
) -> ChatsResponse:
    new_chat = await add_new_chat(user_id=user_id, title=None, session=session)
    return new_chat

@router.delete("/{chat_id}", response_model=ChatDeleteResponse)
async def delete_chat(
    chat_id: int,
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db)
) -> ChatDeleteResponse:
    # Implement the logic to delete the chat
    # You can use a service function similar to get_chats_by_user_id
    response = await delete_chat_by_id(chat_id=chat_id, user_id=user_id, session=session)
    return response