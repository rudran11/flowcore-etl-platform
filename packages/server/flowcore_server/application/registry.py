import threading
from abc import ABC, abstractmethod
from typing import Dict, Optional
from flowcore_shared.schemas.operational.execution import ExecutionRun

class AbstractRunRegistry(ABC):
    """
    Abstract interface for managing execution runs.
    Ensures backend replaceability (e.g., InMemory -> Postgres -> Redis).
    """
    @abstractmethod
    def create_run(self, run: ExecutionRun) -> None:
        pass

    @abstractmethod
    def get_run(self, run_id: str) -> ExecutionRun:
        pass

    @abstractmethod
    def save(self, run: ExecutionRun) -> None:
        pass
        
    @abstractmethod
    def close(self) -> None:
        pass

class InMemoryRunRegistry(AbstractRunRegistry):
    """
    Thread-safe in-memory implementation of AbstractRunRegistry.
    Intended for Milestone 4 before a persistent database is introduced.
    """
    def __init__(self):
        self._runs: Dict[str, ExecutionRun] = {}
        self._lock = threading.Lock()

    def create_run(self, run: ExecutionRun) -> None:
        with self._lock:
            if run.id in self._runs:
                raise ValueError(f"Run {run.id} already exists.")
            self._runs[run.id] = run

    def get_run(self, run_id: str) -> ExecutionRun:
        with self._lock:
            if run_id not in self._runs:
                raise ValueError(f"Run {run_id} not found.")
            return self._runs[run_id]

    def save(self, run: ExecutionRun) -> None:
        with self._lock:
            if run.id not in self._runs:
                raise ValueError(f"Run {run.id} not found. Cannot save.")
            self._runs[run.id] = run
            
    def close(self) -> None:
        # In memory does not require resource cleanup
        pass
