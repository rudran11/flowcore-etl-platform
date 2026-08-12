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
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        user_id: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc"
    ) -> PipelinePaginatedResponse:
        async with self.uow as uow:
            items = await uow.pipelines.list_pipelines(skip, limit, search, tags, folder_id, is_archived, is_favorite, user_id, sort_by, sort_order)
            total = await uow.pipelines.count_pipelines(search, tags, folder_id, is_archived, is_favorite, user_id)
            
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

    async def create_pipeline(self, request: "flowcore_server.models.pipeline.PipelineCreate", owner: str) -> "flowcore.models.pipeline.Pipeline":
        import uuid
        from flowcore.models.pipeline import Pipeline
        from flowcore_server.dependencies.context import get_workspace_id
        
        async with self.uow as uow:
            pipeline = Pipeline(
                id=str(uuid.uuid4()),
                workspace_id=get_workspace_id(),
                owner=owner,
                name=request.name,
                description=request.description,
                tags=request.tags or [],
                folder_id=request.folder_id,
                icon=request.icon,
                color=request.color,
                is_archived=False
            )
            saved_pipeline = await uow.pipelines.create_pipeline(pipeline)
            await uow.commit()
            return saved_pipeline
            
    async def update_pipeline(self, pipeline_id: str, request: "flowcore_server.models.pipeline.PipelineUpdate") -> "flowcore.models.pipeline.Pipeline":
        async with self.uow as uow:
            updates = request.model_dump(exclude_unset=True)
            if not updates:
                pipeline = await uow.pipelines.get_pipeline(pipeline_id)
                if not pipeline:
                    raise ResourceNotFoundError(f"Pipeline with ID {pipeline_id} not found")
                return pipeline
                
            updated_pipeline = await uow.pipelines.update_pipeline(pipeline_id, updates)
            if not updated_pipeline:
                raise ResourceNotFoundError(f"Pipeline with ID {pipeline_id} not found")
                
            await uow.commit()
            return updated_pipeline
            
    async def delete_pipeline(self, pipeline_id: str) -> bool:
        async with self.uow as uow:
            success = await uow.pipelines.delete_pipeline(pipeline_id)
            if not success:
                raise ResourceNotFoundError(f"Pipeline with ID {pipeline_id} not found")
            await uow.commit()
            return True

    async def create_pipeline_version(self, pipeline_id: str, request: "flowcore_server.models.pipeline_version.PipelineVersionCreate") -> "flowcore.models.pipeline.PipelineVersion":
        import uuid
        from flowcore.models.pipeline import PipelineVersion
        from flowcore.models.pipeline.execution_step import ExecutionStep
        
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

    async def toggle_favorite(self, pipeline_id: str, user_id: str, is_favorite: bool) -> None:
        # For a full implementation, we'd have a UserPipelineFavorite repo, but we can do it directly or add a method.
        # Since I haven't added it to repo yet, I will add it to the repo interface and postgres implementation next.
        async with self.uow as uow:
            await uow.pipelines.set_favorite(pipeline_id, user_id, is_favorite)
            await uow.commit()

    async def bulk_delete(self, pipeline_ids: List[str]) -> int:
        count = 0
        async with self.uow as uow:
            for pid in pipeline_ids:
                if await uow.pipelines.delete_pipeline(pid):
                    count += 1
            await uow.commit()
        return count
        
    async def bulk_archive(self, pipeline_ids: List[str], archive: bool) -> int:
        count = 0
        async with self.uow as uow:
            for pid in pipeline_ids:
                updated = await uow.pipelines.update_pipeline(pid, {"is_archived": archive})
                if updated:
                    count += 1
            await uow.commit()
        return count
        
    async def bulk_move(self, pipeline_ids: List[str], folder_id: Optional[str]) -> int:
        count = 0
        async with self.uow as uow:
            for pid in pipeline_ids:
                updated = await uow.pipelines.update_pipeline(pid, {"folder_id": folder_id})
                if updated:
                    count += 1
            await uow.commit()
        return count
