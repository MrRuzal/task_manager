from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from .config import settings
from app.common.logs import logger
from sqlalchemy.exc import SQLAlchemyError

engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    echo=getattr(settings, "DB_ECHO", False),
)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db


async def shutdown():
    await engine.dispose()


async def check_db_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
