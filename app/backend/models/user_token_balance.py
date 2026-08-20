from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from .base import Base


class UserTokenBalance(Base):
    __tablename__ = "user_token_balances"

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    model_name: Mapped[str] = mapped_column(String(100))
    balance: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('userId', 'model_name', name='uq_user_model_balance'),
    )