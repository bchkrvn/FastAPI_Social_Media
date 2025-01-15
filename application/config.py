import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    DEBUG = os.getenv("DEBUG", False)
    PROJECT_NAME = "Social Media"
    PROJECT_VERSION = "1.0.0"
    PROJECT_HOST = os.getenv("PROJECT_HOST", "localhost")
    PROJECT_PORT = os.getenv("PROJECT_PORT", "8000")

    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("DB_HOST", "0.0.0.0")
    POSTGRES_PORT = os.getenv("DB_PORT", 5432)
    POSTGRES_DB = os.getenv("POSTGRES_DB", "social")
    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


settings = Settings()
