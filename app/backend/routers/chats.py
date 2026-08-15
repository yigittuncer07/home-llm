#backend/routers/chats.py
from fastapi import APIRouter, Depends
from auth.dependencies import require_auth_token
from services.chats import get_chats_by_user_id
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.chat import ChatsResponse

router = APIRouter()

@router.get("", response_model=ChatsResponse)
async def get_chats(
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db)
) -> ChatsResponse:
    chats = await get_chats_by_user_id(user_id=user_id, session=session)
    return chats