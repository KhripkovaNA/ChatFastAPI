from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.chat.models import Messages
from app.dao.base import BaseDAO
from app.database import connection
from app.users.models import Users


class UsersDAO(BaseDAO[Users]):
    model = Users

    @classmethod
    @connection
    async def find_all_with_new_messages(
            cls, current_user_id: int, session: AsyncSession
    ) -> list[dict]:
        # Найти всех пользователей с количеством непрочитанных сообщений
        try:
            cte = (
                select(
                    Messages.sender_id,
                    func.count().label("new_mes_count"),
                )
                .filter(and_(Messages.recipient_id == current_user_id, Messages.is_read == False))
                .group_by(Messages.sender_id)
            ).cte()

            query = (
                select(Users.id,
                       Users.name,
                       Users.role,
                       cte.c.new_mes_count)
                .join(cte, cte.c.sender_id == Users.id, isouter=True)
            )

            result = await session.execute(query)
            records = [
                {'id': user.id,
                 'name': user.name,
                 'role': user.role,
                 'new_mes_count': user.new_mes_count or 0}
                for user in result.all()]
            if records:
                logger.info(f"Найдено пользователей: {len(records)}")
            else:
                logger.info(f"Пользователей не найдено")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске пользователей: {e}")
            raise
