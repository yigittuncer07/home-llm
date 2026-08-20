from typing import Any


class AppException(Exception):
    """Base class for all custom API exceptions."""
    def __init__(self, status_code: int, detail: str, log_message: str = ""):
        self.status_code = status_code
        self.detail = detail
        self.log_message = log_message or detail

class InvalidCredentialsError(AppException):
    def __init__(self, email: str, log_message: str = ""):
        super().__init__(
            status_code=401,
            detail="Incorrect email or password",
            log_message=log_message
        )

class UserAlreadyExistsError(AppException):
    def __init__(self, email: str, log_message: str = ""):
        super().__init__(
            status_code=400,
            detail=f"User with email {email} already exists",
            log_message=log_message
        )

class InvalidTokenError(AppException):
    def __init__(self, log_message: str = ""):
        super().__init__(
            status_code=401,
            detail="Invalid or expired token",
            log_message=log_message
        )

class ChatNotFoundError(AppException):
    def __init__(self, chat_id: int, log_message: str = ""):
        super().__init__(
            status_code=404,
            detail=f"Chat with ID {chat_id} not found",
            log_message=log_message
        )
    
class PermissionDeniedError(AppException):
    def __init__(self, log_message: str = ""):
        super().__init__(
            status_code=403,
            detail="Permission denied",
            log_message=log_message
        )

class InternalServerError(AppException):
    def __init__(self, log_message: str = ""):
        super().__init__(
            status_code=500,
            detail="Internal server error",
            log_message=log_message
        )

class LLMAPIError(AppException):
    """Raised when the LLM API responds with an HTTP error status."""
    def __init__(self, chat_id: int, api_status_code: int, api_error_body: str, log_message: str = "", headers: dict[str, Any] | None = None):
        self.chat_id = chat_id
        self.api_status_code = api_status_code
        self.api_error_body = api_error_body
        self.headers = headers or {}
        super().__init__(
            status_code=502, 
            detail="The language model service returned an error",
            log_message=log_message or (
                f"LLM API error for chat {chat_id}: "
                f"upstream status {api_status_code}, body: {api_error_body}"
            )
        )


class LLMConnectionError(AppException):
    """Raised when the LLM API can't be reached at all (network/DNS/timeout)."""
    def __init__(self, chat_id: int, original_error: Exception, log_message: str = ""):
        self.chat_id = chat_id
        self.original_error = original_error
        super().__init__(
            status_code=503,  
            detail="Could not connect to the language model service",
            log_message=log_message or (
                f"Network error connecting to LLM API for chat {chat_id}: "
                f"{type(original_error).__name__} - {original_error}"
            )
        )