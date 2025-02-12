import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def get_bool_env(name: str) -> bool:
    return os.getenv(name, False) in {"True", "true", "t", "T", "1", 1}


class BaseSettings:
    """Базовый режим"""

    DEBUG = False
    DB_DEBUG = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
    PROJECT_NAME = "Social Media"
    PROJECT_VERSION = "1.0.0"
    PROJECT_HOST = os.getenv("PROJECT_HOST", "0.0.0.0")
    PROJECT_PORT = os.getenv("PROJECT_PORT", "8000")
    PAGE_LIMIT = os.getenv("PAGE_LIMIT", 25)

    # Настройки безопасности:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    PASSWORD_LENGTH = os.getenv("PASSWORD_LENGTH", 8)

    # Настройки подключения к БД
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("DB_HOST", "0.0.0.0")
    POSTGRES_PORT = os.getenv("DB_PORT", 5432)
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    def __str__(self):
        return self.__doc__


class DevSettings(BaseSettings):
    """Разработка"""

    DEBUG = get_bool_env("DEBUG")
    DB_DEBUG = get_bool_env("DB_DEBUG")


class TestSettings(BaseSettings):
    """Тестирование"""

    DEBUG = False

    # Настройки безопасности:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))


class ProdSettings(BaseSettings):
    """Прод"""

    DEBUG = False


def get_settings() -> BaseSettings:
    dev = get_bool_env("DEV")
    test = get_bool_env("TEST")

    assert not all((dev, test)), "Установлен и режим тестирования, и режим разработки. Можно выбрать только один режим"

    if test:
        return TestSettings()
    elif dev:
        return DevSettings()
    else:
        return ProdSettings()


settings = get_settings()
