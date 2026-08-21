from models.user_token_balance import UserTokenBalanceItem
from repository.user_token_balance import UserTokenBalanceRepository
from sqlalchemy.ext.asyncio import AsyncSession
from core.logger import logger

async def get_models_service(user_id: str, session: AsyncSession) -> list[UserTokenBalanceItem]:
    token_repo = UserTokenBalanceRepository(session)
    
    balances = await token_repo.get_all_by_user_id(int(user_id))
    
    logger.info(f"Retrieved {len(balances)} model balances for user {user_id}")
    
    return [UserTokenBalanceItem.model_validate(b) for b in balances]