from fastapi import APIRouter, Depends, Path, status
from flowcore_server.models.execution import ExecutionResponse
from flowcore_server.application.execution_app import ExecutionApp
from flowcore_server.dependencies.execution import get_execution_app

router = APIRouter(prefix="/runs", tags=["Runs"])

@router.get(
    "/{run_id}",
    response_model=ExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get execution run status"
)
async def get_run_status(
    run_id: str = Path(..., description="The ID of the execution run"),
    app: ExecutionApp = Depends(get_execution_app)
):
    """
    Retrieves the current state and outputs of an execution run.
    """
    return await app.get_run_status(run_id)

@router.post(
    "/{run_id}/cancel",
    response_model=ExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an execution run"
)
async def cancel_run(
    run_id: str = Path(..., description="The ID of the execution run to cancel"),
    app: ExecutionApp = Depends(get_execution_app)
):
    """
    Cancels an ongoing execution run.
    """
    return await app.cancel_run(run_id)
