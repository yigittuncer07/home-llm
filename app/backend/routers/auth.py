#backend/routers/auth.py
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.auth import LoginRequest, LoginResponse
from services.auth import authenticate_user

router = APIRouter()

@router.post('/login')
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    token = await authenticate_user(request.email, request.password, db)
    return LoginResponse(access_token=token)