#backend/repository/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from sqlalchemy.orm import selectinload

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> User:
        self.session.add(user)        
        await self.session.flush()
        await self.session.refresh(user, attribute_names=["token_balances"])
        return user

    async def get_by_id(self, user_id: int) -> User | None:
            result = await self.session.execute(
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.token_balances))
            )
            return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self.session.execute(
            select(User).options(selectinload(User.token_balances))
        )
        return list(result.scalars().all())
    
    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()