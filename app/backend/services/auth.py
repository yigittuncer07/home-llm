#backend/services/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import verify_password, generate_jwt_token
from repository.user import UserRepository
from core.exceptions import InvalidCredentialsError

async def authenticate_user(email: str, password: str, session: AsyncSession) -> str:
    user_repository = UserRepository(session)
    user = await user_repository.get_by_email(email)
    
    if not user:
        raise InvalidCredentialsError(email, log_message=f"User with email {email} not found")
    
    if not verify_password(password, user.password_hash.encode('utf-8')):
        raise InvalidCredentialsError(email, log_message=f"Invalid password for user with email: {email} ID: {user.id}")

    if user.is_admin:
        return generate_jwt_token(user_id=str(user.id), role="admin")
    
    return generate_jwt_token(user_id=str(user.id), role="user")