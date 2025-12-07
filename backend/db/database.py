"""
Database connection and session management.
Использует SQLAlchemy 2.0 async API для работы с PostgreSQL на Railway.
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from backend.config import get_settings

# Naming convention for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

# Global engine and session maker
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    """
    Получить URL базы данных с правильным драйвером.

    Railway предоставляет DATABASE_URL с postgresql://,
    но для async нужен postgresql+asyncpg://

    Returns:
        str: Database URL с asyncpg драйвером
    """
    settings = get_settings()
    db_url = str(settings.database_url)

    # Replace postgresql:// with postgresql+asyncpg://
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

    return db_url


def create_engine() -> AsyncEngine:
    """
    Создать async engine для SQLAlchemy.

    Returns:
        AsyncEngine: Async database engine
    """
    settings = get_settings()
    db_url = get_database_url()

    # Engine configuration for Railway.com
    engine = create_async_engine(
        db_url,
        echo=settings.is_development,  # Log SQL in development
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Connection pool size
        max_overflow=10,  # Max overflow connections
        pool_recycle=3600,  # Recycle connections after 1 hour
        poolclass=NullPool if settings.is_testing else None,  # No pool for tests
    )

    return engine


def get_engine() -> AsyncEngine:
    """
    Получить или создать async engine.

    Returns:
        AsyncEngine: Database engine
    """
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Получить или создать session maker.

    Returns:
        async_sessionmaker: Session maker
    """
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения database session в FastAPI.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
        ```
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализировать базу данных (создать таблицы).
    Используется для тестов. В production используем Alembic миграции.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Закрыть соединение с базой данных.
    """
    global _engine, _async_session_maker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
    _async_session_maker = None



