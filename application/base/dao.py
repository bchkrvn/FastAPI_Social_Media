from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from application.config import settings
from application.db.base_model import Base
from application.db.session import connection


class BaseDAO:
    model: Base

    @classmethod
    @connection
    async def find_all(
        cls,
        session: AsyncSession,
        filters: dict[str, Any] = None,
        order_by: list[str] = None,
        page: int = 1,
    ) -> list:
        limit = page * settings.PAGE_LIMIT
        offset = (page - 1) * settings.PAGE_LIMIT
        order_by = order_by or ["id"]
        filters = filters or {}

        query = select(cls.model).filter_by(**filters).limit(limit).offset(offset).order_by(*order_by)
        objects = await session.execute(query)
        return objects.scalars().all()

    @classmethod
    @connection
    async def find_one_or_none(cls, session: AsyncSession, **filters):
        query = select(cls.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    @connection
    async def add(cls, session: AsyncSession, **data):
        new_object = cls.model(**data)
        session.add(new_object)
        await session.commit()
        return new_object

    @classmethod
    @connection
    async def update(cls, instance: Base, session: AsyncSession, **data):
        unknown_fields = set(data) - instance.all_fields
        if unknown_fields:
            raise TypeError(f"Model {cls.model.__name__} has not fields: {', '.join(unknown_fields)}")

        for key, value in data.items():
            setattr(instance, key, value)

        session.add(instance)
        await session.commit()
        return instance

    @classmethod
    @connection
    async def delete(cls, instance: Base, session: AsyncSession) -> None:
        await session.delete(instance)
        await session.commit()
