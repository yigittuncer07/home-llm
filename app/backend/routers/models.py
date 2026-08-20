#backend/routers/models.py
from fastapi import APIRouter, Depends, status
from auth.dependencies import require_auth_token
from services.messages import enqueue_message
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.message import SendMessageRequest, ChatHistoryResponse
from services.messages import get_chat_history_service
from services.models import get_models_service

router = APIRouter()

@router.get("")
async def get_models():
    models = await get_models_service()
    return models