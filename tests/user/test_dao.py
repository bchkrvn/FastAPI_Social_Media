import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.user.dao import UserDAO
from application.user.model import User


class TestUserDAO:
    @pytest.mark.anyio
    async def test_find_all_active_user(self, session: AsyncSession):
        user_count = 6
        for i in range(user_count):
            data = {
                "email": f"test{i}@test.ru",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
                "is_active": i % 2 == 0,
            }
            user = User(**data)
            session.add(user)
        await session.commit()

        users = await UserDAO.find_all_active_user()

        assert len(users) == user_count / 2

    @pytest.mark.anyio
    async def test_deactivate(self, user: User):
        assert user.is_active
        await UserDAO.deactivate(user)
        not_active_user = await UserDAO.find_one_or_none(filters=dict(id=user.id))
        assert not_active_user.id == user.id
        assert not not_active_user.is_active

    @pytest.mark.anyio
    async def test_activate(self, user: User, session: AsyncSession):
        await UserDAO.deactivate(user)
        not_active_user = await UserDAO.find_one_or_none(filters=dict(id=user.id))
        assert not not_active_user.is_active
        assert not_active_user.id == user.id

        await UserDAO.activate(user)

        active_user = await UserDAO.find_one_or_none(filters=dict(id=user.id))
        assert active_user.id == user.id
        assert active_user.is_active
