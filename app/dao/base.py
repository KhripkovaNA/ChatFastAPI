from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from app.database import connection
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
        query = select(cls.model).filter_by(id=data_id)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        if not record:
            logger.info(f"Запись {cls.model.__name__} с ID {data_id} не найдена")
        return record

    @classmethod
    @connection
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        # Найти одну запись по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        query = select(cls.model).filter_by(**filter_dict)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        if not record:
            logger.info(f"Запись {cls.model.__name__} не найдена по фильтрам: {filter_dict}")
        return record

    @classmethod
    @connection
    async def find_all(cls, session: AsyncSession, filters: Optional[BaseModel] = None):
        # Если фильтры не заданы, получаем все записи
        if filters is None:
            query = select(cls.model)
        else:
            # Найти все записи по фильтрам
            filter_dict = filters.model_dump(exclude_unset=True)
            query = select(cls.model).filter_by(**filter_dict)
        result = await session.execute(query)
        records = result.scalars().all()
        if not records:
            logger.info(f"Не найдено записей {cls.model.__name__}")
        return records

    @classmethod
    @connection
    async def add(cls, session: AsyncSession, values: BaseModel):
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        await session.commit()
        logger.info(f"Запись {cls.model.__name__} успешно добавлена")

        return new_instance

    @classmethod
    @connection
    async def add_many(cls, session: AsyncSession, instances: List[BaseModel]):
        # Добавить несколько записей
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        new_instances = [cls.model(**values) for values in values_list]
        session.add_all(new_instances)
        await session.commit()
        logger.info(f"Успешно добавлено записей {cls.model.__name__}:  {len(new_instances)}")
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
        result = await session.execute(query)
        await session.commit()
        logger.info(f"Обновлено записей {cls.model.__name__}: {result.rowcount}")
        return result.rowcount

    @classmethod
    @connection
    async def delete(cls, session: AsyncSession, filters: BaseModel):
        # Удалить записи по фильтру
        filter_dict = filters.model_dump(exclude_unset=True)
        if not filter_dict:
            raise ValueError("Нужен хотя бы один фильтр для удаления")

        query = sqlalchemy_delete(cls.model).filter_by(**filter_dict)
        result = await session.execute(query)
        await session.commit()
        logger.info(f"Удалено записей {cls.model.__name__}: {result.rowcount}")
        return result.rowcount
