"""
Pytest configuration and fixtures for testing.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["TELEGRAM_BOT_TOKEN"] = "test:token"
os.environ["ENVIRONMENT"] = "testing"

from backend.main import app
from backend.db.database import Base, get_session
from backend.config import Settings, get_settings


# Override settings for testing
def get_test_settings() -> Settings:
    """Get test settings with in-memory database."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        openai_api_key="sk-test-key",
        telegram_bot_token="test:token",
        environment="testing",
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    settings = get_test_settings()

    # Use in-memory SQLite for tests (faster)
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database session override."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = get_test_settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "ui_language": "ru",
        "level": "beginner",
    }


@pytest.fixture
def user_update_data() -> dict[str, Any]:
    """Sample user update data."""
    return {
        "level": "intermediate",
        "ui_language": "uk",
    }


@pytest.fixture
def settings_update_data() -> dict[str, Any]:
    """Sample settings update data."""
    return {
        "conversation_style": "tutor",
        "voice_speed": "slow",
        "corrections_level": "detailed",
    }

