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

    async def execution_summary(self) -> dict:
        summary = {state.value: 0 for state in ExecutionState}
        for run in self._runs.values():
            summary[run.status.value] += 1
        return summary

    async def daily_execution_counts(self, days: int = 7) -> List[dict]:
        from datetime import datetime, timedelta
        from collections import defaultdict

        now = datetime.utcnow()
        date_counts = defaultdict(lambda: {state.value: 0 for state in ExecutionState})
        
        for run in self._runs.values():
            if run.start_time:
                date_str = run.start_time.strftime("%Y-%m-%d")
                date_counts[date_str][run.status.value] += 1

        result = []
        for i in range(days):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            res = {"date": d}
            res.update(date_counts[d])
            result.append(res)
            
        return result[::-1]

    async def average_duration_ms(self) -> float:
        durations = []
        for run in self._runs.values():
            if run.status == ExecutionState.COMPLETED and run.start_time and run.end_time:
                durations.append((run.end_time - run.start_time).total_seconds() * 1000)
        return sum(durations) / len(durations) if durations else 0.0

    async def recent_runs(self, limit: int = 10, offset: int = 0) -> List[ExecutionRun]:
        sorted_runs = sorted(self._runs.values(), key=lambda r: r.created_at or datetime.utcnow(), reverse=True)
        return sorted_runs[offset:offset+limit]
