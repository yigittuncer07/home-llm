from fastapi import APIRouter, Depends
from auth.dependencies import require_auth_token
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.user_token_balance import UserTokenBalanceItem
from services.models import get_models_service

router = APIRouter()

@router.get("", response_model=list[UserTokenBalanceItem])
async def get_models(user_id: str = Depends(require_auth_token), session: AsyncSession = Depends(get_db)) -> list[UserTokenBalanceItem]:
    models = await get_models_service(user_id, session)
    return models