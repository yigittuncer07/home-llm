#backend/routers/auth.py
from fastapi import Depends, APIRouter

from database import get_db
from models.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from services.auth import authenticate_user, register_user

router = APIRouter()

@router.post('/login')
def login(request: LoginRequest, db=Depends(get_db)) -> LoginResponse:
    token = authenticate_user(request.email, request.password, db)
    return LoginResponse(access_token=token)

    
@router.post('/register')
def register(request: RegisterRequest, db=Depends(get_db)) -> RegisterResponse:
    message = register_user(request.email, request.password, db)
    return RegisterResponse(message=message)