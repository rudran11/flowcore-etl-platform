from fastapi import BackgroundTasks, Depends
from flowcore_server.application.registry import AbstractRunRegistry, InMemoryRunRegistry
from flowcore_server.application.background import BackgroundExecutionStrategy, FastAPIBackgroundStrategy
from flowcore_server.application.pipeline_repo import AbstractPipelineRepository, InMemoryPipelineRepository
from flowcore_server.application.cancellation import CancellationStrategy, InMemoryCancellationStrategy
from flowcore_server.application.engine_factory import ExecutionEngineFactory, DefaultExecutionEngineFactory

# Singleton instances for infrastructure dependencies
_run_registry_instance = InMemoryRunRegistry()
_pipeline_repo_instance = InMemoryPipelineRepository()
_cancellation_instance = InMemoryCancellationStrategy(_run_registry_instance)
_engine_factory_instance = DefaultExecutionEngineFactory()

def get_run_registry() -> AbstractRunRegistry:
    return _run_registry_instance

def get_pipeline_repository() -> AbstractPipelineRepository:
    return _pipeline_repo_instance

def get_cancellation_strategy() -> CancellationStrategy:
    return _cancellation_instance

def get_engine_factory() -> ExecutionEngineFactory:
    return _engine_factory_instance

def get_background_strategy(bt: BackgroundTasks) -> BackgroundExecutionStrategy:
    """
    Dependency yielding the BackgroundExecutionStrategy.
    Wraps FastAPI's BackgroundTasks automatically.
    """
    return FastAPIBackgroundStrategy(bt)
