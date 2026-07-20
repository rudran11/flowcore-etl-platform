from typing import Dict, Any, Optional
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_server.models.execution import ExecutionResponse

def map_execution_to_response(run: ExecutionRun, outputs: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> ExecutionResponse:
    """
    Maps an internal Shared ExecutionRun to a public API ExecutionResponse DTO.
    """
    duration_ms = None
    if run.start_time and run.end_time:
        duration_ms = int((run.end_time - run.start_time).total_seconds() * 1000)

    return ExecutionResponse(
        run_id=run.id,
        pipeline_id=run.pipeline_id,
        status=run.status.value,
        started_at=run.start_time,
        finished_at=run.end_time,
        duration_ms=duration_ms,
        error=error,
        outputs=outputs or {}
    )
