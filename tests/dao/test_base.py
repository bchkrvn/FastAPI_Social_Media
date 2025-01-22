import datetime

import pytest
from sqlalchemy.exc import MultipleResultsFound

from application.dao.base import BaseDAO
from application.user.model import User


class FakeDAO(BaseDAO):
    model = User


class TestBaseDAO:
    dao = FakeDAO

    @pytest.mark.anyio
    async def test_find_all(self, session):
        user_count = 5
        for i in range(user_count):
            data = {
                "email": f"test{i}@test.ru",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
            }
            user = User(**data)
            session.add(user)
        session.commit()

        users = await FakeDAO.find_all()

        assert len(users) == user_count

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
        session.commit()

        users = await FakeDAO.find_all(is_active=True)

        assert len(users) == user_count / 2

    @pytest.mark.anyio
    async def test_find_one(self, user):
        finded_user = await FakeDAO.find_one_or_none(id=user.id)

        assert finded_user.id == user.id

    @pytest.mark.anyio
    async def test_find_one_when_many(self, session):
        user_count = 2
        for i in range(user_count):
            data = {
                "email": f"test{i}@test.ru",
                "password": "1234",
                "first_name": "test_name",
                "last_name": "test_lastname",
                "date_of_birth": datetime.date(year=2025, day=1, month=1),
            }
            user = User(**data)
            session.add(user)
        session.commit()

        with pytest.raises(MultipleResultsFound):
            await FakeDAO.find_one_or_none(first_name="test_name")

    @pytest.mark.anyio
    async def test_find_none(self, user):
        finded_user = await FakeDAO.find_one_or_none(id=99999)
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

        for f in data:
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
