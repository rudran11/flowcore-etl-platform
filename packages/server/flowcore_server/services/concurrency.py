# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional
from flowcore_shared.schemas.base.enums import ConcurrencyPolicy, ExecutionState
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork

class ConcurrencyLimitExceeded(Exception):
    """Raised when workspace concurrency limit is exceeded."""
    pass

class PipelineConcurrencyRejected(Exception):
    """Raised when a pipeline run is rejected due to REJECT policy."""
    pass

class ConcurrencyManager:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def evaluate_run(
        self, 
        workspace_id: str, 
        pipeline_id: str, 
        policy: ConcurrencyPolicy,
        max_workspace_runs: int
    ) -> ExecutionState:
        """
        Evaluates whether a run can start immediately, should queue, or be rejected.
        Returns the initial ExecutionState for the run.
        """
        async with self.uow:
            active_pipeline_runs, _ = await self.uow.executions.list_runs(
                pipeline_id=pipeline_id,
                status=",".join([ExecutionState.PENDING.value, ExecutionState.RUNNING.value, ExecutionState.RETRYING.value])
            )
            
            if len(active_pipeline_runs) > 0:
                if policy == ConcurrencyPolicy.REJECT:
                    raise PipelineConcurrencyRejected(f"Pipeline {pipeline_id} is already running.")
                elif policy == ConcurrencyPolicy.QUEUE:
                    return ExecutionState.QUEUED
                    
            return ExecutionState.PENDING

    async def release_and_dequeue(self, pipeline_id: str) -> Optional[str]:
        """
        Called when a pipeline finishes. Checks if there are QUEUED runs for this pipeline,
        and returns the ID of the next run to start.
        """
        async with self.uow:
            queued_runs, _ = await self.uow.executions.list_runs(
                pipeline_id=pipeline_id,
                status=ExecutionState.QUEUED.value
            )
            print(f"[DEBUG concurrency.py] queued_runs type: {type(queued_runs)}, content: {queued_runs}")
            if queued_runs:
                # We can't rely on created_at as ExecutionRun schema doesn't have it explicitly right now, 
                # but we can just take the first one returned
                return queued_runs[0].id
            return None
