from typing import TypeVar, Generic, List, Any
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from app.database import async_session_maker, connection
from app.database import Base
from loguru import logger

# Объявляем типовой параметр T с ограничением, что это наследник Base
T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    @connection
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        # Найти запись по ID
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с ID {data_id} найдена")
            else:
                logger.info(f"Запись с ID {data_id} не найдена")
            return record

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    @classmethod
    @connection
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        # Найти одну запись по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись найдена по фильтрам: {filter_dict}")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter_dict}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    @connection
    async def find_all(cls, session: AsyncSession, filters: BaseModel):
        # Найти все записи по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            records = result.scalars().all()
            if records:
                logger.info(f"Найдено {len(records)} записей по фильтрам: {filter_dict}")
            else:
                logger.info(f"Не найдено записей по фильтрам: {filter_dict}")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    @connection
    async def add(cls, session: AsyncSession, values: BaseModel):
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.commit()
            logger.info(f"Запись {cls.model.__name__} успешно добавлена")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise
        return new_instance

    @classmethod
    @connection
    async def add_many(cls, session: AsyncSession, instances: List[BaseModel]):
        # Добавить несколько записей
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        new_instances = [cls.model(**values) for values in values_list]
        session.add_all(new_instances)
        try:
            await session.commit()
            logger.info(f"Успешно добавлено {len(new_instances)} записей")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise
        return new_instances

    @classmethod
    @connection
    async def update(cls, session: AsyncSession, filters: BaseModel, values: BaseModel):
        # Обновить записи по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_dict.items()])
            .values(**values_dict)
            .execution_options(synchronize_session="fetch")
        )
        try:
            result = await session.execute(query)
            await session.commit()
            logger.info(f"Обновлено {result.rowcount} записей")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise

    @classmethod
    @connection
    async def delete(cls, session: AsyncSession, filters: BaseModel):
        # Удалить записи по фильтру
        filter_dict = filters.model_dump(exclude_unset=True)
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления")
            raise ValueError("Нужен хотя бы один фильтр для удаления")

        query = sqlalchemy_delete(cls.model).filter_by(**filter_dict)
        try:
            result = await session.execute(query)
            await session.commit()
            logger.info(f"Удалено {result.rowcount} записей")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise

    @classmethod
    @connection
    async def count(cls, session: AsyncSession, filters: BaseModel):
        # Подсчитать количество записей
        filter_dict = filters.model_dump(exclude_unset=True)
        try:
            query = select(func.count(cls.model.id)).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise

    @classmethod
    @connection
    async def paginate(cls, session: AsyncSession, page: int = 1, page_size: int = 10, filters: BaseModel = None):
        # Пагинация записей
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query.offset((page - 1) * page_size).limit(page_size))
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей на странице {page}")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при пагинации записей: {e}")
            raise

    @classmethod
    @connection
    async def find_by_ids(cls, session: AsyncSession, ids: List[int]) -> List[Any]:
        # Найти несколько записей по списку ID
        logger.info(f"Поиск записей {cls.model.__name__} по списку ID: {ids}")
        try:
            query = select(cls.model).filter(cls.model.id.in_(ids))
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей по списку ID")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записей по списку ID: {e}")
            raise
