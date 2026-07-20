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

    def start_pipeline_execution(self, pipeline_id: str, version: str, request: ExecutionRequest) -> ExecutionResponse:
        run = self.service.start_execution(
            pipeline_id=pipeline_id,
            version=version,
            trigger_type="API",
            parameters=request.parameters
        )
        return map_execution_to_response(run)

    def get_run_status(self, run_id: str) -> ExecutionResponse:
        run = self.service.get_execution(run_id)
        return map_execution_to_response(run)

    def cancel_run(self, run_id: str) -> ExecutionResponse:
        self.service.cancel_execution(run_id)
        run = self.service.get_execution(run_id)
        return map_execution_to_response(run)
