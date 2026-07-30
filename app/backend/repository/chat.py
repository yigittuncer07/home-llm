from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.chat import Chat

class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, chat: Chat) -> Chat:
        self.session.add(chat)
        self.session.flush()
        return chat

    def get_by_id(self, chat_id: int) -> Chat | None:
        return self.session.get(Chat, chat_id)

    def get_by_user_id(self, user_id: int) -> Sequence[Chat]:
        stmt = select(Chat).where(Chat.user_id == user_id)
        return self.session.scalars(stmt).all()