#backend/routers/auth.py
from fastapi import Depends, Header, HTTPException, APIRouter

from database import get_db
from auth.security import validate_jwt_token, generate_jwt_token
from models.auth import LoginRequest, LoginResponse
from services.auth import authenticate_user

router = APIRouter()

def require_auth_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token_string = authorization.split(' ')[1]
    
    payload = validate_jwt_token(token_string)

    if not payload:
        raise HTTPException(status_code=401, detail="Token invalid or experid")
    
    return payload["sub"]

@router.post('/login')
def login(request: LoginRequest, db=Depends(get_db)) -> LoginResponse:
    token = authenticate_user(request.email, request.password, db)
    return LoginResponse(access_token=token)