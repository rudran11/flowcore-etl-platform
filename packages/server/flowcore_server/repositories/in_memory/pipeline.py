from typing import List, Optional
from flowcore.models.pipeline import Pipeline, PipelineVersion
from flowcore_server.repositories.interfaces.pipeline import AbstractPipelineRepository

class InMemoryPipelineRepository(AbstractPipelineRepository):
    def __init__(self):
        self._pipelines = {}
        self._versions = {}

    async def create_pipeline(self, pipeline: Pipeline) -> Pipeline:
        self._pipelines[pipeline.id] = pipeline
        return pipeline

    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        return self._pipelines.get(pipeline_id)

    async def update_pipeline(self, pipeline_id: str, updates: dict) -> Optional[Pipeline]:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return None
            
        for key, value in updates.items():
            if hasattr(pipeline, key):
                setattr(pipeline, key, value)
                
        self._pipelines[pipeline_id] = pipeline
        return pipeline
        
    async def get_pipeline_by_name(self, name: str) -> Optional[Pipeline]:
        for p in self._pipelines.values():
            if p.name == name:
                return p
        return None

    async def list_pipelines(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Pipeline]:
        pipelines = list(self._pipelines.values())
        if search:
            search_lower = search.lower()
            pipelines = [p for p in pipelines if search_lower in p.name.lower() or (p.description and search_lower in p.description.lower())]
        if tags:
            pipelines = [p for p in pipelines if all(tag in p.tags for tag in tags)]
        return pipelines[skip : skip + limit]

    async def delete_pipeline(self, pipeline_id: str) -> bool:
        if pipeline_id in self._pipelines:
            del self._pipelines[pipeline_id]
            return True
        return False

    async def create_pipeline_version(self, version: PipelineVersion) -> PipelineVersion:
        self._versions[(version.pipeline_id, version.version)] = version
        return version

    async def get_pipeline_version(self, pipeline_id: str, version_tag: str) -> Optional[PipelineVersion]:
        return self._versions.get((pipeline_id, version_tag))

    async def get_pipeline_version_by_id(self, version_id: str) -> Optional[PipelineVersion]:
        for v in self._versions.values():
            if v.id == version_id:
                return v
        return None

    async def list_pipeline_versions(self, pipeline_id: str) -> List[PipelineVersion]:
        return [v for v in self._versions.values() if str(v.pipeline_id) == pipeline_id]

    async def count_pipelines(
        self,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        pipelines = list(self._pipelines.values())
        if search:
            search_lower = search.lower()
            pipelines = [p for p in pipelines if search_lower in p.name.lower() or (p.description and search_lower in p.description.lower())]
        if tags:
            pipelines = [p for p in pipelines if all(tag in p.tags for tag in tags)]
        return len(pipelines)
