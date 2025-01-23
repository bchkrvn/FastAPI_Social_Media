from sqlalchemy.ext.asyncio import AsyncSession

from application.dao.base import BaseDAO

from ..db.session import connection
from .model import User


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    @connection
    async def delete(cls, instance: User, session: AsyncSession) -> None:
        instance.is_active = False
        session.add(instance)
        await session.commit()
