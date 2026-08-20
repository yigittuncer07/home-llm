#backend/routers/admin.py
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import require_admin_token
from database import get_db
from models.user import UserResponse
from services.admin import get_all_users_service, delete_user_service

router = APIRouter()

@router.get('/users', response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> list[UserResponse]:
    users = await get_all_users_service(db)
    return users

@router.delete('/users/{user_id}', response_model=UserResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(require_admin_token)) -> UserResponse:
    deleted_user = await delete_user_service(db, user_id)
    return deleted_user