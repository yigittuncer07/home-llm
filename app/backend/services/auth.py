#backend/services/auth.py

import logging

from fastapi import HTTPException, Header
from auth.security import validate_jwt_token, verify_password, generate_jwt_token, hash_password
from repository.user import UserRepository
from models.user import User
from core.exceptions import InvalidCredentialsError, UserAlreadyExistsError

def require_auth_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token_string = authorization.split(' ')[1]
    
    payload = validate_jwt_token(token_string)

    if not payload:
        raise HTTPException(status_code=401, detail="Token invalid or experid")
    
    return payload["sub"]

def authenticate_user(email: str, password: str, session) -> str:
    user_repository = UserRepository(session)
    user = user_repository.get_by_email(email)
    
    if not user:
        raise InvalidCredentialsError(email, log_message=f"User with email {email} not found")
    
    if not verify_password(password, user.password_hash.encode('utf-8')):
        raise InvalidCredentialsError(email, log_message=f"Invalid password for user with email: {email} ID: {user.id}")
    
    return generate_jwt_token(user_id=str(user.id), role="user")
    
def register_user(email: str, password: str, session) -> str:
    user_repository = UserRepository(session)
    user = user_repository.get_by_email(email)
    
    if user:
        raise UserAlreadyExistsError(email, log_message=f"Attempt to register existing user with email: {email} ID: {user.id}")

    user = user_repository.add(
        User(
            email=email,
            password_hash=hash_password(password)
        )
    )
    logging.info(f"User registered with email: {email} ID: {user.id}")

    return "User registered successfully"

    