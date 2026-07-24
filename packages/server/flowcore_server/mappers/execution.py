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

    links = {
        "self": f"/api/v1/runs/{run.id}",
        "cancel": f"/api/v1/runs/{run.id}/cancel"
    }

    from flowcore_server.models.execution import ExecutionStepResponse
    
    mapped_steps = {}
    for step_id, step in run.steps.items():
        step_duration_ms = None
        if step.start_time and step.end_time:
            step_duration_ms = int((step.end_time - step.start_time).total_seconds() * 1000)
        
        mapped_steps[step_id] = ExecutionStepResponse(
            step_id=step.step_id,
            status=step.status.value,
            start_time=step.start_time,
            end_time=step.end_time,
            duration_ms=step_duration_ms,
            retry_count=step.retry_count,
            error_message=step.error_message,
            outputs=step.outputs,
            logs=step.logs
        )

    return ExecutionResponse(
        run_id=run.id,
        pipeline_id=run.pipeline_id,
        pipeline_version=run.pipeline_version_id,
        status=run.status.value,
        submitted_at=run.created_at,
        started_at=run.start_time,
        finished_at=run.end_time,
        duration_ms=duration_ms,
        error=run.error_message or error,
        outputs=run.outputs or outputs or {},
        steps=mapped_steps,
        links=links
    )
