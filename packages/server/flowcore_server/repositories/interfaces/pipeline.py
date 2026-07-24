import abc
from typing import List, Optional
from flowcore_shared.schemas.pipeline import Pipeline, PipelineVersion

class AbstractPipelineRepository(abc.ABC):
    """
    Abstract repository for Pipeline metadata operations.
    Exclusively returns and consumes Domain Models (flowcore_shared.schemas).
    """

    @abc.abstractmethod
    async def create_pipeline(self, pipeline: Pipeline) -> Pipeline:
        pass

    @abc.abstractmethod
    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        pass
        
    @abc.abstractmethod
    async def get_pipeline_by_name(self, name: str) -> Optional[Pipeline]:
        pass

    @abc.abstractmethod
    async def list_pipelines(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Pipeline]:
        pass

    @abc.abstractmethod
    async def delete_pipeline(self, pipeline_id: str) -> bool:
        pass

    @abc.abstractmethod
    async def create_pipeline_version(self, version: PipelineVersion) -> PipelineVersion:
        pass

    @abc.abstractmethod
    async def get_pipeline_version(self, pipeline_id: str, version_tag: str) -> Optional[PipelineVersion]:
        pass

    @abc.abstractmethod
    async def get_pipeline_version_by_id(self, version_id: str) -> Optional[PipelineVersion]:
        pass

    @abc.abstractmethod
    async def list_pipeline_versions(self, pipeline_id: str) -> List[PipelineVersion]:
        pass

    @abc.abstractmethod
    async def count_pipelines(
        self,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        pass
