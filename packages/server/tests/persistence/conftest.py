import pytest
import pytest_asyncio
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from flowcore_server.config.settings import settings
from flowcore_server.repositories.postgres.uow import AsyncSqlAlchemyUnitOfWork
from flowcore_server.repositories.in_memory.uow import InMemoryUnitOfWork

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy.pool import NullPool

# Use the real database for integration testing
# Tests will run inside a transaction and rollback
test_engine = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

@pytest_asyncio.fixture
async def pg_uow():
    """Yields a Postgres UoW that rolls back after the test."""
    uow = AsyncSqlAlchemyUnitOfWork(session_factory=TestSessionLocal)
    async with uow:
        yield uow
        await uow.rollback()  # Always rollback to keep DB clean

@pytest_asyncio.fixture
async def in_mem_uow():
    """Yields a fresh InMemory UoW."""
    uow = InMemoryUnitOfWork()
    async with uow:
        yield uow

@pytest.fixture(params=["pg_uow", "in_mem_uow"])
def any_uow(request):
    """Parameterize tests to run against both implementations."""
    return request.getfixturevalue(request.param)
