from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Message(Base):
    __tablename__ = "messages"
    
    message_id: Mapped[int] = mapped_column("messageId", primary_key=True)
    chat_id: Mapped[int] = mapped_column("chatId", ForeignKey("chats.chatId", ondelete="CASCADE"))
    model: Mapped[str] = mapped_column(String(100))
    tokens: Mapped[int]
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())