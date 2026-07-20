import abc
from typing import List, Optional
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState

class AbstractExecutionRepository(abc.ABC):
    """
    Abstract repository for Execution Run operations.
    Exclusively returns and consumes Domain Models (flowcore_shared.schemas).
    """

    @abc.abstractmethod
    async def create_run(self, run: ExecutionRun) -> ExecutionRun:
        pass

    @abc.abstractmethod
    async def get_run(self, run_id: str) -> Optional[ExecutionRun]:
        pass

    @abc.abstractmethod
    async def list_runs_for_pipeline(self, pipeline_id: str, limit: int = 100, offset: int = 0) -> List[ExecutionRun]:
        pass

    @abc.abstractmethod
    async def update_run_status(self, run_id: str, status: ExecutionState) -> bool:
        pass

    @abc.abstractmethod
    async def save(self, run: ExecutionRun) -> ExecutionRun:
        """Upsert operation for saving an entire run object."""
        pass

    @abc.abstractmethod
    async def execution_summary(self) -> dict:
        """Returns a dict of counts by ExecutionState."""
        pass

    @abc.abstractmethod
    async def daily_execution_counts(self, days: int = 7) -> List[dict]:
        """Returns a list of dicts with 'date' and counts by state."""
        pass

    @abc.abstractmethod
    async def average_duration_ms(self) -> float:
        """Returns the average duration in milliseconds of all completed runs."""
        pass

    @abc.abstractmethod
    async def recent_runs(self, limit: int = 10, offset: int = 0) -> List[ExecutionRun]:
        """Returns the most recent runs across all pipelines."""
        pass
