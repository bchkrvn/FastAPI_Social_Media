from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from application.db.session import connection


class BaseDAO:
    model = None

    @classmethod
    @connection
    async def find_all(cls, session: AsyncSession, **filters):
        query = select(cls.model).filter_by(**filters)
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
    async def add(cls, session: AsyncSession, **data) -> model:
        new_object = cls.model(**data)
        session.add(new_object)
        await session.commit()
        return new_object
