from models.user_token_balance import UserTokenBalanceItem
from repository.user_token_balance import UserTokenBalanceRepository
from sqlalchemy.ext.asyncio import AsyncSession
from core.logger import logger
from config import settings

async def get_models_service(user_id: str, session: AsyncSession) -> list[UserTokenBalanceItem]:
    token_repo = UserTokenBalanceRepository(session)
    
    # get existing balances from DB
    db_balances = await token_repo.get_all_by_user_id(int(user_id))
    
    # create a lookup dictionary for fast matching
    balance_lookup = {b.model_name: b.balance for b in db_balances}
    
    # build the list using all configured models, defaulting to 0 if not in DB
    result = []
    for model_name in settings.models_config.keys():
        balance = balance_lookup.get(model_name, 0)
        result.append(UserTokenBalanceItem(model_name=model_name, balance=balance))
        
    logger.info(f"Retrieved {len(result)} model balances for user {user_id}")
    
    return result