from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from .base import Base

class Chat(Base):
    __tablename__ = "chats"
    
    chat_id: Mapped[int] = mapped_column("chatId", primary_key=True)
    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(255))