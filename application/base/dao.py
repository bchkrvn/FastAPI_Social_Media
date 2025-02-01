from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from application.config import settings
from application.db.base_model import Base
from application.db.session import connection


class BaseDAO:
    model: Base
    options = []

    @classmethod
    @connection
    async def find_all(
        cls,
        session: AsyncSession,
        filters: dict[str, Any] = None,
        order_by: list[str] = None,
        options: list = None,
        page: int = 1,
    ) -> list:
        limit = page * settings.PAGE_LIMIT
        offset = (page - 1) * settings.PAGE_LIMIT
        order_by = order_by or ["id"]
        filters = filters or {}
        options = options or []
        all_options = cls.options + options

        q = select(cls.model).filter_by(**filters)
        q = q.limit(limit).offset(offset)
        q = q.order_by(*order_by)
        q = q.options(*all_options)

        objects = await session.execute(q)
        return objects.scalars().all()

    @classmethod
    @connection
    async def find_one_or_none(cls, session: AsyncSession, filters: dict[str, Any], options: list = None):
        options = options or []
        all_options = cls.options + options
        query = select(cls.model).filter_by(**filters).options(*all_options)
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
