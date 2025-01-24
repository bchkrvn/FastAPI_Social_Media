from sqlalchemy.ext.asyncio import AsyncSession

from application.base.dao import BaseDAO
from application.db.session import connection

from .model import User


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def find_all_active_user(cls, **filters) -> list[User]:
        filters["is_active"] = True
        return await cls.find_all(**filters)

    @classmethod
    @connection
    async def deactivate(cls, instance: User, session: AsyncSession) -> None:
        instance.is_active = False
        session.add(instance)
        await session.commit()

    @classmethod
    @connection
    async def activate(cls, instance: User, session: AsyncSession) -> None:
        instance.is_active = True
        session.add(instance)
        await session.commit()
