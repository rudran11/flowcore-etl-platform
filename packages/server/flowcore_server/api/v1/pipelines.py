from fastapi import APIRouter, Depends, Path, status
from flowcore_server.models.execution import ExecutionRequest, ExecutionResponse
from flowcore_server.application.execution_app import ExecutionApp
from flowcore_server.dependencies.execution import get_execution_app
from flowcore_server.dependencies.auth import require_permissions, UserInDB

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
    app: ExecutionApp = Depends(get_execution_app),
    user: UserInDB = Depends(require_permissions(["pipeline:execute"]))
):
    """
    Asynchronously executes a specific version of a pipeline with the provided runtime parameters.
    Returns a 202 Accepted status along with the run ID for status tracking.
    """
    return await app.start_pipeline_execution(pipeline_id, version, request)

from typing import Optional, List
from fastapi import Query
from flowcore_server.models.pipeline import PipelinePaginatedResponse, PipelineDetailResponse, PipelineCreate, PipelineUpdate
from flowcore.models.pipeline import Pipeline
from flowcore_server.services.pipeline import PipelineService
from flowcore_server.dependencies.pipeline import get_pipeline_service

@router.post(
    "",
    response_model=Pipeline,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pipeline"
)
async def create_pipeline(
    request: PipelineCreate,
    service: PipelineService = Depends(get_pipeline_service),
    user: UserInDB = Depends(require_permissions(["pipeline:create"]))
):
    """
    Creates a new pipeline.
    """
    return await service.create_pipeline(request, user.username)

@router.put(
    "/{pipeline_id}",
    response_model=Pipeline,
    status_code=status.HTTP_200_OK,
    summary="Update pipeline metadata"
)
async def update_pipeline(
    request: PipelineUpdate,
    pipeline_id: str = Path(..., description="The ID of the pipeline"),
    service: PipelineService = Depends(get_pipeline_service),
    user: UserInDB = Depends(require_permissions(["pipeline:update"]))
):
    """
    Updates pipeline metadata.
    """
    return await service.update_pipeline(pipeline_id, request)

@router.delete(
    "/{pipeline_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pipeline"
)
async def delete_pipeline(
    pipeline_id: str = Path(..., description="The ID of the pipeline"),
    service: PipelineService = Depends(get_pipeline_service),
    user: UserInDB = Depends(require_permissions(["pipeline:delete"]))
):
    """
    Deletes a pipeline.
    """
    await service.delete_pipeline(pipeline_id)


@router.get(
    "",
    response_model=PipelinePaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="List pipelines"
)
async def list_pipelines(
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination limit"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    tags: Optional[List[str]] = Query(None, description="Tags to filter by"),
    service: PipelineService = Depends(get_pipeline_service),
    user: UserInDB = Depends(require_permissions([]))
):
    """
    Retrieves a paginated list of pipelines.
    Supports filtering by search term and tags.
    """
    return await service.list_pipelines(skip=skip, limit=limit, search=search, tags=tags)

@router.get(
    "/{pipeline_id}",
    response_model=PipelineDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pipeline details"
)
async def get_pipeline(
    pipeline_id: str = Path(..., description="The ID of the pipeline"),
    service: PipelineService = Depends(get_pipeline_service)
):
    """
    Retrieves details for a specific pipeline including versions and recent runs.
    """
    return await service.get_pipeline_details(pipeline_id)

from flowcore_server.models.pipeline_version import PipelineVersionCreate, PipelineVersionResponse

@router.post(
    "/{pipeline_id}/versions",
    response_model=PipelineVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new pipeline version"
)
async def save_pipeline_version(
    request: PipelineVersionCreate,
    pipeline_id: str = Path(..., description="The ID of the pipeline"),
    service: PipelineService = Depends(get_pipeline_service)
):
    """
    Saves a new pipeline version (e.g. from the builder).
    """
    return await service.create_pipeline_version(pipeline_id, request)
