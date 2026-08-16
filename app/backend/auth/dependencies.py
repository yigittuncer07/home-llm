from fastapi import HTTPException, Header
from auth.security import validate_jwt_token
from core.exceptions import InvalidTokenError

def require_auth_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise InvalidTokenError(log_message="Invalid token format, expected 'Bearer <token>'")

    token_string = authorization.split(' ')[1]
    
    payload = validate_jwt_token(token_string)

    if not payload:
        raise InvalidTokenError(log_message="Token invalid or expired, failed to validate")
    
    return payload["sub"]