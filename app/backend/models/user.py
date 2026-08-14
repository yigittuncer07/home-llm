from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from models.chat import Chat
from models.user_config import UserConfig
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(200))
    
    chats: Mapped[list["Chat"]] = relationship(cascade="all, delete-orphan")
    config: Mapped["UserConfig"] = relationship(cascade="all, delete-orphan")