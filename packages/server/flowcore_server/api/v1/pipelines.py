from fastapi import APIRouter, Depends, Path, status
from flowcore_server.models.execution import ExecutionRequest, ExecutionResponse
from flowcore_server.application.execution_app import ExecutionApp
from flowcore_server.dependencies.execution import get_execution_app

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])

@router.post(
    "/{pipeline_id}/versions/{version}/execute",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a pipeline execution"
)
async def execute_pipeline(
    request: ExecutionRequest,
    pipeline_id: str = Path(..., description="The ID of the pipeline to execute"),
    version: str = Path(..., description="The specific version of the pipeline"),
    app: ExecutionApp = Depends(get_execution_app)
):
    """
    Asynchronously executes a specific version of a pipeline with the provided runtime parameters.
    Returns a 202 Accepted status along with the run ID for status tracking.
    """
    return app.start_pipeline_execution(pipeline_id, version, request)
