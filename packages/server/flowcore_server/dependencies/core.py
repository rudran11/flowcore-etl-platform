from fastapi import BackgroundTasks, Depends
from flowcore_server.application.background import BackgroundExecutionStrategy, FastAPIBackgroundStrategy
from flowcore_server.application.cancellation import CancellationStrategy, DefaultCancellationStrategy
from flowcore_server.application.engine_factory import ExecutionEngineFactory, DefaultExecutionEngineFactory
from flowcore_server.repositories.factory import RepositoryFactory
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.application.interfaces.dispatcher import AbstractEventDispatcher
from flowcore_server.application.dispatchers.in_memory import InMemoryEventDispatcher

# Singleton instances for infrastructure dependencies
_repository_factory = RepositoryFactory(use_postgres=True) # Will inject Postgres by default
_cancellation_instance = DefaultCancellationStrategy()
_engine_factory_instance = DefaultExecutionEngineFactory()
_event_dispatcher_instance = InMemoryEventDispatcher()

async def get_uow() -> AbstractUnitOfWork:
    """Dependency yielding the Unit of Work."""
    uow = _repository_factory.get_unit_of_work()
    # We yield it so FastAPI doesn't necessarily manage the context block here since 
    # the application services will use `async with uow:` themselves.
    return uow

def get_cancellation_strategy() -> CancellationStrategy:
    return _cancellation_instance

def get_engine_factory() -> ExecutionEngineFactory:
    return _engine_factory_instance

def get_event_dispatcher() -> AbstractEventDispatcher:
    return _event_dispatcher_instance

def get_background_strategy(bt: BackgroundTasks) -> BackgroundExecutionStrategy:
    """
    Dependency yielding the BackgroundExecutionStrategy.
    Wraps FastAPI's BackgroundTasks automatically.
    """
    return FastAPIBackgroundStrategy(bt)
