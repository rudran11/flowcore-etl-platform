from abc import ABC, abstractmethod
from typing import Protocol, Callable, Any, Optional
from dataclasses import dataclass
from fastapi import BackgroundTasks

@dataclass
class TaskHandle:
    """
    A handle representing an asynchronous background task.
    Allows for future extensions like checking status or canceling jobs.
    """
    task_id: str
    status: str = "PENDING"

class BackgroundExecutionStrategy(Protocol):
    """
    Abstract protocol for background task dispatching.
    Replaceable with Celery, Kubernetes Jobs, AWS Batch, etc.
    """
    def submit(self, func: Callable, *args: Any, **kwargs: Any) -> TaskHandle:
        ...
        
    def shutdown(self) -> None:
        ...

class FastAPIBackgroundStrategy:
    """
    Implementation of BackgroundExecutionStrategy that wraps FastAPI's BackgroundTasks.
    """
    def __init__(self, bt: BackgroundTasks):
        self._bt = bt

    def submit(self, func: Callable, *args: Any, **kwargs: Any) -> TaskHandle:
        self._bt.add_task(func, *args, **kwargs)
        # We return a dummy handle since FastAPI's BackgroundTasks doesn't provide IDs
        return TaskHandle(task_id="fastapi-task")
        
    def shutdown(self) -> None:
        # FastAPI handles graceful shutdown of internal background tasks automatically
        pass
