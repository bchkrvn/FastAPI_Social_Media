import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class BaseSettings:
    DEBUG = False
    PROJECT_NAME = "Social Media"
    PROJECT_VERSION = "1.0.0"
    PROJECT_HOST = os.getenv("PROJECT_HOST", "localhost")
    PROJECT_PORT = os.getenv("PROJECT_PORT", "8000")
    PAGE_LIMIT = os.getenv("PAGE_LIMIT", 25)

    # Настройки безопасности:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

    # Настройки подключения к БД
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("DB_HOST", "0.0.0.0")
    POSTGRES_PORT = os.getenv("DB_PORT", 5432)
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


class DevSettings(BaseSettings):
    DEBUG = True


class TestSettings(BaseSettings):
    DEBUG = False

    # Настройки безопасности:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))

    # Настройки подключения к БД
    TEST_DATABASE_URL = (
        f"postgresql://{BaseSettings.POSTGRES_USER}:{BaseSettings.POSTGRES_PASSWORD}@{BaseSettings.POSTGRES_HOST}:"
        f"{BaseSettings.POSTGRES_PORT}/{BaseSettings.POSTGRES_DB}"
    )


class ProdSettings(BaseSettings):
    DEBUG = False


def get_settings() -> BaseSettings:
    dev = os.getenv("DEV") == "True"
    test = os.getenv("TEST") == "True"

    if test:
        return TestSettings()
    elif dev:
        return DevSettings()
    else:
        return ProdSettings()


settings = get_settings()
