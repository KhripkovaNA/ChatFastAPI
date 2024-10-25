from datetime import datetime
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.config import settings

database_url = settings.DATABASE_URL
engine = create_async_engine(database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Decorator automatically creates and handles the session for database operations
def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)  # Pass session to the decorated method
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    return wrapper


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @classmethod
    @property
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
