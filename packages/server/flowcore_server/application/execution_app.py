from typing import Optional
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.models.execution import ExecutionRequest, ExecutionResponse
from flowcore_server.mappers.execution import map_execution_to_response

class ExecutionApp:
    """
    Application logic for pipeline execution.
    Orchestrates mapping DTOs to service calls.
    """
    def __init__(self, execution_service: ExecutionService):
        self.service = execution_service

    async def start_pipeline_execution(self, pipeline_id: str, version: str, request: ExecutionRequest) -> ExecutionResponse:
        run = await self.service.start_execution(
            pipeline_id=pipeline_id,
            version=version,
            trigger_type="API",
            parameters=request.parameters
        )
        return map_execution_to_response(run)

    async def get_run_status(self, run_id: str) -> ExecutionResponse:
        run = await self.service.get_execution(run_id)
        if not run:
            from flowcore_server.application.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError("Run not found")
        return map_execution_to_response(run)

    async def cancel_run(self, run_id: str) -> ExecutionResponse:
        await self.service.cancel_execution(run_id)
        run = await self.service.get_execution(run_id)
        return map_execution_to_response(run)

    async def list_runs(
        self, 
        pipeline_id: Optional[str] = None, 
        status: Optional[str] = None, 
        limit: int = 25, 
        skip: int = 0
    ):
        from flowcore_server.models.execution import ExecutionListResponse
        runs, total = await self.service.list_executions(
            pipeline_id=pipeline_id,
            status=status,
            limit=limit,
            skip=skip
        )
        return ExecutionListResponse(
            items=[map_execution_to_response(r) for r in runs],
            total=total,
            limit=limit,
            skip=skip
        )
