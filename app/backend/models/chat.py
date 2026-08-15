#backend/models/chat.py

from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from models.base import Base
from pydantic import BaseModel, ConfigDict

# to prevent circular import issue
if TYPE_CHECKING:
    from models.message import Message

# ORM model for the Chat table
class Chat(Base):
    __tablename__ = "chats"
    
    chat_id: Mapped[int] = mapped_column("chatId", primary_key=True)
    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(255))
    
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")


# pydantic model for the Chat response for the GET /chats endpoint
class ChatItem(BaseModel):
    chat_id: int
    user_id: int
    title: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ChatsResponse(BaseModel):
    chats: list[ChatItem]
    
# pydantic model for the Chat response and request for the POST /chats endpoint
class ChatCreateRequest(BaseModel):
    title: str | None = None
    
# pydantic model for the DELETE /chats/{chat_id} endpoint
class ChatDeleteResponse(BaseModel):
    message: str