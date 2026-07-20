from typing import Optional
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork

class RepositoryFactory:
    """
    Factory for instantiating the correct UnitOfWork implementation.
    This hides implementation selection from the Application Layer.
    """
    def __init__(self, use_postgres: bool = True):
        self.use_postgres = use_postgres
        self._in_memory_uow: Optional[AbstractUnitOfWork] = None

    def get_unit_of_work(self) -> AbstractUnitOfWork:
        if self.use_postgres:
            # Import locally to avoid importing SQLAlchemy models if this factory is configured to be in-memory
            from flowcore_server.repositories.postgres.uow import AsyncSqlAlchemyUnitOfWork
            return AsyncSqlAlchemyUnitOfWork()
        else:
            if self._in_memory_uow is None:
                from flowcore_server.repositories.in_memory.uow import InMemoryUnitOfWork
                # InMemory UoW is a singleton in the factory context so state persists across requests
                self._in_memory_uow = InMemoryUnitOfWork()
            return self._in_memory_uow
