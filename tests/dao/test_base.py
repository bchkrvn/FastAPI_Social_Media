import datetime

import pytest
from sqlalchemy.exc import MultipleResultsFound

from application.base.dao import BaseDAO
from application.config import settings
from application.user.model import User


class FakeDAO(BaseDAO):
    model = User


class TestBaseDAO:
    dao = FakeDAO

    @pytest.fixture(scope="function", autouse=True)
    def drop(self, drop_user_table):
        yield

    async def create_users(self, user_count, session, **kwargs):
        for i in range(user_count):
            data = {
                "email": f"test{i}@test.ru",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
                **kwargs,
            }
            user = User(**data)
            session.add(user)
        await session.commit()

    @pytest.mark.anyio
    async def test_find_all(self, session):
        user_count = 5
        await self.create_users(user_count, session)

        users = await FakeDAO.find_all()

        assert len(users) == user_count

    @pytest.mark.anyio
    async def test_find_all_first_page_not_enough(self, session):
        user_count = settings.PAGE_LIMIT - 1
        await self.create_users(user_count, session)

        users = await FakeDAO.find_all()

        assert len(users) == user_count

    @pytest.mark.anyio
    async def test_find_all_first_page_many(self, session):
        user_count = settings.PAGE_LIMIT + 1
        await self.create_users(user_count, session)

        users_1 = await FakeDAO.find_all()
        users_2 = await FakeDAO.find_all(page=1)

        assert len(users_1) == settings.PAGE_LIMIT
        assert len(users_2) == settings.PAGE_LIMIT

    @pytest.mark.anyio
    async def test_find_all_last_page(self, session):
        user_count = settings.PAGE_LIMIT + 1
        await self.create_users(user_count, session)

        users = await FakeDAO.find_all(page=2)

        assert len(users) == 1

    @pytest.mark.anyio
    async def test_find_all_filter(self, session):
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

        users = await FakeDAO.find_all(filters=dict(is_active=True))

        assert len(users) == user_count / 2

    @pytest.mark.anyio
    async def test_find_one(self, user):
        filters = dict(id=user.id)
        finded_user = await FakeDAO.find_one_or_none(filters=filters)

        assert finded_user.id == user.id

    @pytest.mark.anyio
    async def test_find_one_when_many(self, session):
        user_count = 2
        await self.create_users(user_count, session)

        with pytest.raises(MultipleResultsFound):
            filters = dict(first_name="test_name")
            await FakeDAO.find_one_or_none(filters=filters)

    @pytest.mark.anyio
    async def test_find_none(self, user):
        filters = dict(id=99999)
        finded_user = await FakeDAO.find_one_or_none(filters=filters)
        assert finded_user is None

    @pytest.mark.anyio
    async def test_add_success(self):
        data = {
            "email": "test@test.ru",
            "password": "1234",
            "first_name": "test_name",
            "last_name": "test_lastname",
            "date_of_birth": datetime.date(year=2025, day=1, month=1),
        }

        user = await FakeDAO.add(**data)

        new_user = await FakeDAO.find_one_or_none(filters={})
        assert isinstance(new_user.id, int)
        for f in data:
            assert getattr(new_user, f) == data[f]
            assert getattr(user, f) == data[f]

    @pytest.mark.anyio
    async def test_add_wrong_field(self):
        data = {
            "wrong": None,
        }
        with pytest.raises(TypeError):
            await FakeDAO.add(**data)

    @pytest.mark.anyio
    async def test_update_success(self, user):
        data = {
            "email": "test2@test.ru",
            "password": "12344321",
            "first_name": "test_name2",
            "last_name": "test_lastname2",
            "date_of_birth": datetime.date(year=2025, day=2, month=2),
        }

        updated_user = await FakeDAO.update(user, **data)

        for f in data:
            assert getattr(updated_user, f) == data[f]

    @pytest.mark.anyio
    async def test_update_wrong_field(self, user):
        data = {
            "wrong": None,
        }

        with pytest.raises(TypeError):
            await FakeDAO.update(user, **data)

    @pytest.mark.anyio
    async def test_delete(self, user, session):
        await FakeDAO.delete(user)

        users = await FakeDAO.find_all()
        assert not users
