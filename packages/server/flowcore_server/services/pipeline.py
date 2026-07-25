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
        from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep
        
        async with self.uow as uow:
            pipeline = await uow.pipelines.get_pipeline(pipeline_id)
            if not pipeline:
                raise ResourceNotFoundError(f"Pipeline with ID {pipeline_id} not found")
                
            steps = []
            if request.dsl_definition and isinstance(request.dsl_definition, dict):
                dsl_steps = request.dsl_definition.get("steps", {})
                for step_id, step_config in dsl_steps.items():
                    # Handle possible None for depends_on
                    depends_on_raw = step_config.get("depends_on") or []
                    depends_on = [dep for dep in depends_on_raw if dep != "trigger" and dep != "Trigger"]
                    
                    steps.append(
                        ExecutionStep(
                            step_id=step_id,
                            connector_id=step_config.get("plugin_id") or step_config.get("type") or "unknown",
                            depends_on=depends_on,
                            parameters=step_config.get("config") or {}
                        )
                    )

            version = PipelineVersion(
                id=str(uuid.uuid4()),
                pipeline_id=pipeline_id,
                version=request.version_tag,
                steps=steps,
                dsl_definition=request.dsl_definition,
                graph_definition=request.graph_definition
            )
            
            saved_version = await uow.pipelines.create_pipeline_version(version)
            await uow.commit()
            return saved_version
