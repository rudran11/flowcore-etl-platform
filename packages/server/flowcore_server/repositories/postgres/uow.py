from sqlalchemy.ext.asyncio import AsyncSession
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.repositories.postgres.pipeline import PostgresPipelineRepository
from flowcore_server.repositories.postgres.execution import PostgresExecutionRepository
from flowcore_server.config.database import AsyncSessionLocal

class AsyncSqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        
    async def __aenter__(self) -> "AsyncSqlAlchemyUnitOfWork":
        self.session: AsyncSession = self.session_factory()
        self._pipelines = PostgresPipelineRepository(self.session)
        self._executions = PostgresExecutionRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @property
    def pipelines(self):
        return self._pipelines
        
    @property
    def executions(self):
        return self._executions
