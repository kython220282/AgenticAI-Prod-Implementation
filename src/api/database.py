"""
Database Configuration and Connection Management
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# Database engine (created on startup)
engine = None
async_session_maker = None


async def init_db() -> None:
    """
    Initialize database connection.
    
    Creates the async engine and session maker.
    """
    global engine, async_session_maker
    
    # Convert postgres:// to postgresql+asyncpg://
    db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(
        db_url,
        echo=settings.DATABASE_ECHO if hasattr(settings, "DATABASE_ECHO") else False,
        pool_size=settings.DATABASE_POOL_SIZE if hasattr(settings, "DATABASE_POOL_SIZE") else 20,
        max_overflow=settings.DATABASE_MAX_OVERFLOW if hasattr(settings, "DATABASE_MAX_OVERFLOW") else 10,
        poolclass=NullPool if "sqlite" in db_url else None,
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("Database connection initialized")


async def close_db() -> None:
    """Close database connections."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
