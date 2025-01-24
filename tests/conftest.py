import datetime
import secrets

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from application.auth.constants import COOKIES_TOKEN_KEY
from application.auth.services import create_access_token
from application.config import settings
from application.db.base_model import Base
from application.main import app
from application.user.dao import UsersDAO
from application.user.model import User
from application.user.password import get_password_hash


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(settings.DATABASE_URL)
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture(scope="session")
async def create(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
async def session(engine, create):
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="function")
async def user(password, drop_user_table) -> User:
    user_data = {
        "email": f"{secrets.token_urlsafe(10)}@test.test",
        "password": get_password_hash(password),
        "first_name": "test_name",
        "last_name": "test_lastname",
        "date_of_birth": datetime.date(year=2025, day=1, month=1),
    }
    return await UsersDAO.add(**user_data)


@pytest.fixture(scope="function")
async def admin(password, drop_user_table) -> User:
    user_data = {
        "email": f"{secrets.token_urlsafe(10)}@test.test",
        "password": get_password_hash(password),
        "first_name": "admin",
        "last_name": "admin",
        "date_of_birth": datetime.date(year=2025, day=1, month=1),
        "is_admin": True,
    }
    return await UsersDAO.add(**user_data)


@pytest.fixture(scope="function")
async def drop_user_table(engine):
    yield
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)
        await conn.run_sync(User.metadata.create_all)
