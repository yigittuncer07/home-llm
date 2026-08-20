#backend/routers/admin.py
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import require_admin_token
from database import get_db
from services.admin import get_all_users_service
from models.user import UserResponse

router = APIRouter()

@router.get('/users', response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db), admin_token: str = Depends(require_admin_token)):
    users = await get_all_users_service(db)
    return users