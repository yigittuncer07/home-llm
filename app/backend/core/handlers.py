# core/handlers.py
from fastapi import Request
from typing import cast
from fastapi.responses import JSONResponse
from .exceptions import AppException
from core.logger import logger


async def app_exception_handler(request: Request, exc: Exception):
    
    exc = cast(AppException, exc)
    
    if exc.status_code >= 500:
        logger.error(exc.log_message)
    else:
        logger.warning(exc.log_message)
        
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )