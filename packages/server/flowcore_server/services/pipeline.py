from typing import List, Optional
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.models.pipeline import PipelinePaginatedResponse, PipelineDetailResponse
from flowcore_server.application.exceptions import ResourceNotFoundError

class PipelineService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def list_pipelines(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> PipelinePaginatedResponse:
        async with self.uow as uow:
            items = await uow.pipelines.list_pipelines(skip, limit, search, tags)
            total = await uow.pipelines.count_pipelines(search, tags)
            
            return PipelinePaginatedResponse(
                items=items,
                total=total,
                skip=skip,
                limit=limit
            )

    async def get_pipeline_details(self, pipeline_id: str) -> PipelineDetailResponse:
        async with self.uow as uow:
            pipeline = await uow.pipelines.get_pipeline(pipeline_id)
            if not pipeline:
                raise ResourceNotFoundError(f"Pipeline with ID {pipeline_id} not found")
                
            versions = await uow.pipelines.list_pipeline_versions(pipeline_id)
            recent_runs = await uow.executions.list_runs_for_pipeline(pipeline_id, limit=5, offset=0)
            
            return PipelineDetailResponse(
                pipeline=pipeline,
                versions=versions,
                recent_runs=recent_runs
            )

    async def create_pipeline_version(self, pipeline_id: str, request: "flowcore_server.models.pipeline_version.PipelineVersionCreate") -> "flowcore_shared.schemas.pipeline.PipelineVersion":
        import uuid
        from flowcore_shared.schemas.pipeline import PipelineVersion
        
        async with self.uow as uow:
            pipeline = await uow.pipelines.get_pipeline(pipeline_id)
            if not pipeline:
                raise ResourceNotFoundError(f"Pipeline with ID {pipeline_id} not found")
                
            version = PipelineVersion(
                id=str(uuid.uuid4()),
                pipeline_id=pipeline_id,
                version=request.version_tag,
                steps=[],  # Will populate later or infer from dsl
                dsl_definition=request.dsl_definition,
                graph_definition=request.graph_definition
            )
            
            saved_version = await uow.pipelines.create_pipeline_version(version)
            await uow.commit()
            return saved_version
