from models.user import UserResponse
from models.user_token_balance import TokenBalanceResponse
from models.chat import Chat
from repository.chat import ChatRepository
from core.exceptions import ChatNotFoundError, PermissionDeniedError
from core.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_token_balance import UserTokenBalanceRepository
from core.exceptions import AppException
from config import settings

async def verify_chat_ownership(chat_id: int, user_id: str, session: AsyncSession) -> Chat:
    chat_repository = ChatRepository(session)
    chat = await chat_repository.get_by_id(chat_id)
    
    if not chat:
        log_message = f"User {user_id} attempted to access non-existent chat {chat_id}"
        logger.error(log_message)
        raise ChatNotFoundError(chat_id=chat_id, log_message=log_message)
    elif chat.user_id != int(user_id):
        log_message = f"User {user_id} attempted to access chat {chat_id} they do not own"
        logger.error(log_message)
        raise PermissionDeniedError(log_message=log_message)
        
    return chat


async def check_and_deduct_tokens(user_id: int, model_name: str, requested_tokens: int, session: AsyncSession) -> None:
    """
    Atomically checks and deducts tokens. 
    Raises a 402 exception if the user's balance is insufficient.
    """
    repo = UserTokenBalanceRepository(session)
    success = await repo.decrement_balance(user_id, model_name, requested_tokens)
    
    if not success:
        log_message = f"Failed to deduct {requested_tokens} tokens for user {user_id} on model {model_name}. Insufficient balance."
        logger.error(log_message)
        raise AppException(
            status_code=402,
            detail=f"Insufficient tokens for model {model_name}.",
            log_message=log_message
        )
        

async def ensure_positive_balance(user_id: int, model_name: str, session: AsyncSession) -> None:
    repo = UserTokenBalanceRepository(session)
    balance = await repo.get_balance(user_id, model_name)
    
    if balance <= 0:
        log_message = f"User {user_id} has depleted token balance for model {model_name}. Current balance: {balance}"
        logger.error(log_message)
        raise AppException(
            status_code=402,
            detail=f"Token balance depleted for model {model_name}.",
            log_message=log_message
        )

        
def backfill_token_balances(response: UserResponse) -> UserResponse:
    """Helper to ensure all configured models are present in the response."""
    existing_balances = {b.model_name: b for b in response.token_balances}
    full_balances = []
    
    for model_name in settings.models_config.keys():
        if model_name in existing_balances:
            full_balances.append(existing_balances[model_name])
        else:
            full_balances.append(
                TokenBalanceResponse(
                    id=0, # placeholder
                    userId=response.id,
                    model_name=model_name,
                    balance=0
                )
            )
            
    response.token_balances = full_balances
    return response