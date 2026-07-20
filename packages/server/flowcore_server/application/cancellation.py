from abc import ABC, abstractmethod
from flowcore_server.application.registry import AbstractRunRegistry
from flowcore_shared.schemas.base.enums import ExecutionState

class CancellationStrategy(ABC):
    """
    Abstract strategy for cancelling an execution run.
    """
    @abstractmethod
    def cancel(self, run_id: str) -> None:
        pass

class InMemoryCancellationStrategy(CancellationStrategy):
    """
    Milestone 4 placeholder. Simply marks the run as CANCELED in the registry.
    """
    def __init__(self, registry: AbstractRunRegistry):
        self.registry = registry

    def cancel(self, run_id: str) -> None:
        run = self.registry.get_run(run_id)
        if run.status not in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]:
            updated_run = run.model_copy(update={"status": ExecutionState.CANCELLED})
            self.registry.save(updated_run)
