from sqlalchemy.ext.asyncio import AsyncSession
from models.user_config import UserConfig

class UserConfigRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, config: UserConfig) -> UserConfig:
        merged_config = await self.session.merge(config)
        await self.session.flush()
        return merged_config

    async def get_by_user_id(self, user_id: int) -> UserConfig | None:
        return await self.session.get(UserConfig, user_id)