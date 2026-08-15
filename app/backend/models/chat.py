from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from models.base import Base

if TYPE_CHECKING:
    from models.message import Message

class Chat(Base):
    __tablename__ = "chats"
    
    chat_id: Mapped[int] = mapped_column("chatId", primary_key=True)
    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(255))
    
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")