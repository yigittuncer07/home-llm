from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_token_balance import UserTokenBalance

class UserTokenBalanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_balance(self, user_id: int, model_name: str) -> int:
        result = await self.session.execute(
            select(UserTokenBalance.balance)
            .where(and_(UserTokenBalance.userId == user_id, UserTokenBalance.model_name == model_name))
        )
        return result.scalar() or 0

    async def decrement_balance(self, user_id: int, model_name: str, amount: int) -> bool:
        """
        Atomically decrements the balance. 
        Returns True if successful, False if balance is insufficient.
        """
        result = await self.session.execute(
            update(UserTokenBalance)
            .where(
                and_(
                    UserTokenBalance.userId == user_id,
                    UserTokenBalance.model_name == model_name,
                )
            )
            .values(balance=UserTokenBalance.balance - amount)
        )
        
        return result.rowcount > 0 # type: ignore