from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from shared_utils.db.base import Base
from shared_utils.core.conf import settings
from shared_utils.utils import safe_call


engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URL
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)


@safe_call
async def init_db() -> None:
    """
    Initializes the database by creating all tables defined in the ORM models.
    This function runs the database schema creation process asynchronously and is wrapped with a safe call decorator.

    This function is typically used to set up the database schema on the first run or when migrating.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@safe_call
async def close_db() -> None:
    """
    Disposes of the asynchronous SQLAlchemy engine, closing all active connections.
    This function is wrapped with a safe call decorator and is used for cleanup when the application shuts down.
    """
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    """
    Provides an asynchronous session for database interaction.
    This function is a generator that yields an active database session, which is used within a context manager.

    The session is automatically closed once the operation is completed.
    """
    async with async_session() as session:
        yield session
