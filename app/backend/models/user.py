from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from models.chat import Chat
from models.user_token_balance import UserTokenBalance
from models.user_config import UserConfig
from .base import Base
from pydantic import BaseModel


# orm object
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(200))
    
    chats: Mapped[list["Chat"]] = relationship(cascade="all, delete-orphan")
    config: Mapped["UserConfig"] = relationship(cascade="all, delete-orphan")
    token_balances: Mapped[list["UserTokenBalance"]] = relationship(cascade="all, delete-orphan")
    is_admin: Mapped[bool] = mapped_column(default=False, server_default='false') # Add this line


# pydantic models
# for get users admin response
class UserResponse(BaseModel):
    id: int
    username: str | None
    email: str
    is_admin: bool

    model_config = {"from_attributes": True}

# class UserCreate(BaseModel):
#     username: str | None
#     email: str
#     password: str
#     is_admin: bool = False

#     model_config = {"from_attributes": True}