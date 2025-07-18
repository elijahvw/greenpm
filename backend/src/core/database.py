"""
Green PM - Database Configuration
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)

# Async Database engine
if settings.DATABASE_URL:
    # Convert PostgreSQL URL to async format for async operations
    async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        async_url,
        echo=settings.ENVIRONMENT == "dev",
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    # Sync engine for migrations
    sync_engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.ENVIRONMENT == "dev",
        pool_pre_ping=True,
        pool_recycle=300,
    )
else:
    # For development/testing without database
    engine = None
    sync_engine = None

# Session factory
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Sync session for migrations
    SessionLocal = sessionmaker(
        sync_engine,
        expire_on_commit=False
    )
else:
    AsyncSessionLocal = None
    SessionLocal = None

# Base class for models
class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )

# Dependency to get database session
async def get_db():
    if not AsyncSessionLocal:
        raise RuntimeError("Database not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()