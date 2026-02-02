"""
Test configuration and fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.api.main import app
from src.api.database import get_db
from src.api.models.base import Base
from src.api.config import get_settings


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for tests."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(async_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    
    async def override_get_db():
        yield async_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """Test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_agent_data() -> dict:
    """Test agent data."""
    return {
        "name": "Test Agent",
        "type": "research",
        "description": "A test research agent",
        "config": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "is_active": True
    }


@pytest.fixture
def test_task_data() -> dict:
    """Test task data."""
    return {
        "title": "Test Task",
        "description": "A test task for the agent",
        "priority": 1
    }


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user_data: dict
) -> AsyncGenerator[tuple[AsyncClient, dict], None]:
    """Create authenticated test client with token."""
    
    # Register user
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Set authorization header
    client.headers["Authorization"] = f"Bearer {access_token}"
    
    yield client, token_data
    
    # Cleanup
    client.headers.pop("Authorization", None)
