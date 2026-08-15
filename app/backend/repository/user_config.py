from sqlalchemy.ext.asyncio import AsyncSession
from models.user_config import UserConfig

class UserConfigRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, config: UserConfig) -> UserConfig:
        self.session.add(config)
        await self.session.flush()
        return config

    async def get_by_user_id(self, user_id: int) -> UserConfig | None:
        return await self.session.get(UserConfig, user_id)