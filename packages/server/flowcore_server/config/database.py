import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .settings import settings

logger = logging.getLogger(__name__)

# Create the async engine
# Note: pool_size, max_overflow, and pool_timeout are used to manage connections efficiently.
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    echo=False,  # Set to True for SQL query logging in development
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncSession:
    """
    FastAPI Dependency to yield a database session.
    Automatically closes the session when the request finishes.
    """
    async with AsyncSessionLocal() as session:
        yield session
