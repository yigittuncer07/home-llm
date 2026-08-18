#backend/routers/messages.py
from fastapi import APIRouter, Depends, status
from auth.dependencies import require_auth_token
from services.messages import enqueue_message
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.message import SendMessageRequest, ChatHistoryResponse
from services.messages import get_chat_history_service

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

@router.get("")
async def get_chat_history(chat_id: int, user_id: str = Depends(require_auth_token), session: AsyncSession = Depends(get_db)) -> ChatHistoryResponse:
    chat_history = await get_chat_history_service(chat_id, user_id, session)
    return chat_history