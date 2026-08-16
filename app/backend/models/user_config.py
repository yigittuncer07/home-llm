#backend/models/user_config.py

from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from pydantic import BaseModel, ConfigDict

# ORM object for user configuration settings
class UserConfig(Base):
    __tablename__ = "user_config"
    
    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    personalized_prompt: Mapped[str] = mapped_column(Text)


# pydantic models for request and response validation
class UserConfigResponse(BaseModel):
    personalized_prompt: str
    model_config = ConfigDict(from_attributes=True)

class UserConfigUpdateRequest(BaseModel):
    personalized_prompt: str