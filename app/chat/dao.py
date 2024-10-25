from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from app.dao.base import BaseDAO
from app.chat.models import Messages
from app.database import connection


class MessagesDAO(BaseDAO[Messages]):
    model = Messages

    @classmethod
    @connection
    async def get_messages_between_users(cls, user_id_1: int, user_id_2: int, session: AsyncSession):
        # Найти все сообщения между двумя пользователями
        query = select(cls.model).filter(
            or_(
                and_(cls.model.sender_id == user_id_1, cls.model.recipient_id == user_id_2),
                and_(cls.model.sender_id == user_id_2, cls.model.recipient_id == user_id_1)
            )
        ).order_by(cls.model.id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    @connection
    async def mark_messages_as_read(cls, sender_id: int, recipient_id: int, session: AsyncSession):
        # Обновить статус всех сообщений между двумя пользователями как прочитанных
        stmt = (
            update(cls.model)
            .values(is_read=True)
            .filter(
               and_(cls.model.sender_id == sender_id,
                    cls.model.recipient_id == recipient_id,
                    cls.model.is_read == False)
                )
            )
        await session.execute(stmt)
        await session.commit()
