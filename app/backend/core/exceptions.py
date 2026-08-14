class AppException(Exception):
    """Base class for all custom API exceptions."""
    def __init__(self, status_code: int, detail: str, log_message: str = ""):
        self.status_code = status_code
        self.detail = detail
        self.log_message = log_message or detail

class InvalidCredentialsError(AppException):
    def __init__(self, username: str):
        super().__init__(
            status_code=401,
            detail="Incorrect username or password",
            log_message=f"Failed login attempt for user: {username}"
        )