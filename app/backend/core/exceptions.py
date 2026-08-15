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