from sqlalchemy import Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Messages(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
