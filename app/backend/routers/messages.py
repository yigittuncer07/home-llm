#backend/routers/messages.py
from fastapi import APIRouter, Depends, status
from auth.dependencies import require_auth_token
from services.chats import get_chats_by_user_id, add_new_chat, delete_chat_by_id, update_chat_title
from services.messages import enqueue_message
from models.chat import ChatUpdateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.message import SendMessageRequest

router = APIRouter()

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def send_message(
    request: SendMessageRequest,
    chat_id: int,
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db),
):
    response = await enqueue_message(request, user_id, chat_id, session)
    return {"message": response}