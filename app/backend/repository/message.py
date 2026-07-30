from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.message import Message

class MessageRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, message: Message) -> Message:
        self.session.add(message)
        self.session.flush()
        return message

    def get_by_chat_id(self, chat_id: int) -> Sequence[Message]:
        stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.timestamp)
        return self.session.scalars(stmt).all()