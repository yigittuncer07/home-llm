from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import Chat

class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, chat: Chat) -> Chat:
        self.session.add(chat)
        await self.session.flush()
        return chat

    async def get_by_id(self, chat_id: int) -> Chat | None:
        return await self.session.get(Chat, chat_id)

    async def get_by_user_id(self, user_id: int) -> Sequence[Chat]:
        stmt = select(Chat).where(Chat.user_id == user_id)
        return (await self.session.scalars(stmt)).all()