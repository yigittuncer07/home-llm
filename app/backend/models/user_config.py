from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class UserConfig(Base):
    __tablename__ = "user_config"
    
    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    personalized_prompt: Mapped[str] = mapped_column(Text)