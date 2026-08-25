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

async def alerting_handler(event):
    import logging
    logger = logging.getLogger("flowcore.alerting")
    logger.critical(f"ALERT: Pipeline Run {event.run_id} failed! Message: {event.error_message}")

_event_dispatcher_instance.register_handler("PipelineExecutionFailed", alerting_handler)

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

_scheduler_instance = None

def get_scheduler_service():
    global _scheduler_instance
    if _scheduler_instance is None:
        from flowcore_server.services.scheduler import SchedulerService
        from flowcore_server.services.execution_service import ExecutionService
        from flowcore_server.application.background import AsyncioBackgroundStrategy
        from flowcore_server.dependencies.engine import get_plugin_manager
        
        uow = _repository_factory.get_unit_of_work()
        pm = get_plugin_manager()
        
        exec_service = ExecutionService(
            uow=uow,
            engine_factory=_engine_factory_instance,
            cancellation_strategy=_cancellation_instance,
            background_strategy=AsyncioBackgroundStrategy(),
            plugin_manager=pm,
            event_dispatcher=_event_dispatcher_instance
        )
        _scheduler_instance = SchedulerService(uow, execution_service=exec_service)
        
    return _scheduler_instance
