import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.auth.services import COOKIES_TOKEN_KEY, create_access_token
from application.config import settings
from application.db.base_model import Base
from application.main import app
from application.user.dao import UsersDAO
from application.user.model import User
from application.user.password import get_password_hash


@pytest.fixture(scope="function", autouse=True)
def session():
    engine = create_engine(settings.TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    with session() as s:
        yield s

    Base.metadata.drop_all(engine)


@pytest.fixture
def password():
    password = "MW~26MQ%E35xwzH"
    return password


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture()
async def auth_client(user) -> AsyncClient:
    cookies = {COOKIES_TOKEN_KEY: create_access_token(user)}
    async with AsyncClient(transport=ASGITransport(app=app), cookies=cookies, base_url="http://test") as client:
        yield client


@pytest.fixture()
async def auth_admin_client(admin) -> AsyncClient:
    cookies = {COOKIES_TOKEN_KEY: create_access_token(admin)}
    async with AsyncClient(transport=ASGITransport(app=app), cookies=cookies, base_url="http://test") as client:
        yield client


@pytest.fixture
async def user(password) -> User:
    user_data = {
        "email": "test@test.ru",
        "password": get_password_hash(password),
        "first_name": "test_name",
        "last_name": "test_lastname",
        "date_of_birth": datetime.date(year=2025, day=1, month=1),
    }
    user = await UsersDAO.add(**user_data)
    return user


@pytest.fixture
async def admin(password) -> User:
    user_data = {
        "email": "test@test.ru",
        "password": get_password_hash(password),
        "first_name": "test_name",
        "last_name": "test_lastname",
        "date_of_birth": datetime.date(year=2025, day=1, month=1),
        "is_admin": True,
    }
    user = await UsersDAO.add(**user_data)
    return user
