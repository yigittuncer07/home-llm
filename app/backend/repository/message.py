#backend/repository/message.py

from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.message import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_by_chat_id(self, chat_id: int) -> Sequence[Message]:
        stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.timestamp)
        return (await self.session.scalars(stmt)).all()