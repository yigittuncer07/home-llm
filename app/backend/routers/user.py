#backend/routers/user.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import require_auth_token
from database import get_db
from models.user_config import UserConfigResponse, UserConfigUpdateRequest
from services.user import get_user_config_service, update_user_config_service

router = APIRouter()

@router.get("/config", response_model=UserConfigResponse)
async def get_user_config(
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db)
) -> UserConfigResponse:
    config = await get_user_config_service(user_id=user_id, session=session)
    return config

@router.patch("/config", response_model=UserConfigResponse)
async def update_user_config(
    request: UserConfigUpdateRequest,
    user_id: str = Depends(require_auth_token),
    session: AsyncSession = Depends(get_db)
) -> UserConfigResponse:
    updated_config = await update_user_config_service(
        user_id=user_id,
        personalized_prompt=request.personalized_prompt,
        session=session
    )
    return updated_config