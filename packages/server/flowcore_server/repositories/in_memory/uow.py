from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.repositories.in_memory.pipeline import InMemoryPipelineRepository
from flowcore_server.repositories.in_memory.execution import InMemoryExecutionRepository

class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        # We instantiate them once so state persists across UoW contexts
        self._pipelines = InMemoryPipelineRepository()
        self._executions = InMemoryExecutionRepository()
        self.committed = False
        
    async def __aenter__(self) -> "InMemoryUnitOfWork":
        self.committed = False
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.committed = False

    @property
    def pipelines(self):
        return self._pipelines
        
    @property
    def executions(self):
        return self._executions
