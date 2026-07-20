from fastapi import BackgroundTasks, Depends
from flowcore_server.application.registry import AbstractRunRegistry, InMemoryRunRegistry
from flowcore_server.application.background import BackgroundExecutionStrategy, FastAPIBackgroundStrategy

# Singleton instances for infrastructure dependencies
_run_registry_instance = InMemoryRunRegistry()

def get_run_registry() -> AbstractRunRegistry:
    """
    Dependency yielding the application's RunRegistry.
    """
    return _run_registry_instance

def get_background_strategy(bt: BackgroundTasks = Depends()) -> BackgroundExecutionStrategy:
    """
    Dependency yielding the BackgroundExecutionStrategy.
    Wraps FastAPI's BackgroundTasks automatically.
    """
    return FastAPIBackgroundStrategy(bt)
