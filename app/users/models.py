from typing import List

from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class UserRole(enum.Enum):
    admin = "admin"
    user = "user"


class Users(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    tg_id: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.user)

    sent_messages: Mapped[List['Messages']] = relationship(
        "Messages", back_populates="sender",
        foreign_keys="[Messages.sender_id]"
    )
    received_messages: Mapped[List['Messages']] = relationship(
        "Messages", back_populates="recipient",
        foreign_keys="[Messages.recipient_id]"
    )

    def __str__(self):
        return f"User {self.email}"
