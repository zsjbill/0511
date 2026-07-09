"""
Dual database connection pools for enterprise_assistant and student_assistant.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config.settings import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ---- Enterprise Assistant Database ----
enterprise_async_engine = create_async_engine(
    settings.ENTERPRISE_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=False,
)
EnterpriseSessionLocal = async_sessionmaker(
    bind=enterprise_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_enterprise_db():
    """FastAPI dependency: yields an enterprise_assistant DB session."""
    async with EnterpriseSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---- Student Assistant Database ----
student_async_engine = create_async_engine(
    settings.STUDENT_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=False,
)
StudentSessionLocal = async_sessionmaker(
    bind=student_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_student_db():
    """FastAPI dependency: yields a student_assistant DB session."""
    async with StudentSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all tables in both databases."""
    async with enterprise_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with student_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose both database engines."""
    await enterprise_async_engine.dispose()
    await student_async_engine.dispose()
