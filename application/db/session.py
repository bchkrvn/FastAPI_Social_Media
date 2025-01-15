from config import settings
from sqlalchemy import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
