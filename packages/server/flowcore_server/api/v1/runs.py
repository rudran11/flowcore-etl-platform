from fastapi import APIRouter, Depends, Path, Query, status
from flowcore_server.models.execution import ExecutionResponse, ExecutionListResponse
from flowcore_server.application.execution_app import ExecutionApp
from flowcore_server.dependencies.execution import get_execution_app
from flowcore_server.dependencies.auth import require_permissions
from flowcore_shared.schemas.auth import Principal
from flowcore_shared.schemas.auth import UserInDB, Principal
from typing import Optional

router = APIRouter(prefix="/runs", tags=["Runs"])

@router.get(
    "",
    response_model=ExecutionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List execution runs"
)
async def list_runs(
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline ID"),
    run_status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(25, ge=1, le=100),
    skip: int = Query(0, ge=0),
    app: ExecutionApp = Depends(get_execution_app),
    principal: Principal = Depends(require_permissions([]))
):
    """
    Retrieves a paginated list of execution runs.
    """
    return await app.list_runs(
        pipeline_id=pipeline_id,
        status=run_status,
        limit=limit,
        skip=skip
    )

@router.get(
    "/{run_id}",
    response_model=ExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get execution run status"
)
async def get_run_status(
    run_id: str = Path(..., description="The ID of the execution run"),
    app: ExecutionApp = Depends(get_execution_app),
    principal: Principal = Depends(require_permissions([]))
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
    app: ExecutionApp = Depends(get_execution_app),
    principal: Principal = Depends(require_permissions(["pipeline:execute"]))
):
    """
    Cancels an ongoing execution run.
    """
    return await app.cancel_run(run_id)
