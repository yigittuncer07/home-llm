#backend/models/message.py

from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.chat import Chat

from models.base import Base

# orm object
class Message(Base):
    __tablename__ = "messages"
    
    message_id: Mapped[int] = mapped_column("messageId", primary_key=True)
    chat_id: Mapped[int] = mapped_column("chatId", ForeignKey("chats.chatId", ondelete="CASCADE"))
    model: Mapped[str] = mapped_column(String(100))
    tokens: Mapped[int] = mapped_column("tokens", nullable=True)
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    
# pydantic model
class SendMessageRequest(BaseModel):
    prompt: str
    model: str

class ChatMessage(BaseModel):
    message_id: int
    chat_id: int
    model: str
    tokens: int | None
    role: str
    content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatHistoryResponse(BaseModel):
    chat_id: int
    messages: list[ChatMessage]