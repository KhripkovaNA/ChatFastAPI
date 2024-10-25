from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
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
