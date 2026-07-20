from typing import List, Optional
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.repositories.interfaces.execution import AbstractExecutionRepository

class InMemoryExecutionRepository(AbstractExecutionRepository):
    def __init__(self):
        self._runs = {}

    async def create_run(self, run: ExecutionRun) -> ExecutionRun:
        self._runs[run.id] = run
        return run

    async def get_run(self, run_id: str) -> Optional[ExecutionRun]:
        return self._runs.get(run_id)

    async def list_runs_for_pipeline(self, pipeline_id: str, limit: int = 100, offset: int = 0) -> List[ExecutionRun]:
        matches = [r for r in self._runs.values() if r.pipeline_id == pipeline_id]
        return matches[offset:offset+limit]

    async def update_run_status(self, run_id: str, status: ExecutionState) -> bool:
        if run_id in self._runs:
            run = self._runs[run_id]
            # Since Domain models are frozen by default, we'd normally recreate or use model_copy(update={})
            # But in memory mock can just replace it
            self._runs[run_id] = run.model_copy(update={"status": status})
            return True
        return False

    async def save(self, run: ExecutionRun) -> ExecutionRun:
        self._runs[run.id] = run
        return run
