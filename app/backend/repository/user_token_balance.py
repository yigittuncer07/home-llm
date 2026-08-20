#/backend/repository/user_token_balance.py
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from core.logger import logger
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

        logger.info(f"Attempting to decrement balance for user {user_id} on model {model_name} by {amount}.")
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

    async def set_balance(self, user_id: int, model_name: str, balance: int) -> UserTokenBalance:
        result = await self.session.execute(
            select(UserTokenBalance)
            .where(
                and_(
                    UserTokenBalance.userId == user_id, 
                    UserTokenBalance.model_name == model_name
                )
            )
        )
        record = result.scalar_one_or_none()

        if record:
            record.balance = balance
        else:
            record = UserTokenBalance(userId=user_id, model_name=model_name, balance=balance)
            self.session.add(record)
            
        await self.session.flush()
        return record
    
    async def get_all_by_user_id(self, user_id: int) -> list[UserTokenBalance]:
        result = await self.session.execute(
            select(UserTokenBalance)
            .where(UserTokenBalance.userId == user_id)
        )
        return list(result.scalars().all())