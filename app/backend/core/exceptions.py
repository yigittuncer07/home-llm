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