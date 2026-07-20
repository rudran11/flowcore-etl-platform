from abc import ABC, abstractmethod
from typing import Optional, Dict
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph

class AbstractPipelineRepository(ABC):
    """
    Abstract interface for retrieving pipeline definitions.
    Ensures backend replaceability (InMemory -> Postgres).
    """
    @abstractmethod
    def get_pipeline_version(self, pipeline_id: str, version: str) -> Optional[PipelineVersion]:
        pass

    @abstractmethod
    def get_dependency_graph(self, pipeline_id: str, version: str) -> Optional[DependencyGraph]:
        pass

class InMemoryPipelineRepository(AbstractPipelineRepository):
    """
    In-memory implementation for Milestone 4.
    """
    def __init__(self):
        self._versions: Dict[str, PipelineVersion] = {}
        self._graphs: Dict[str, DependencyGraph] = {}

    def _key(self, pipeline_id: str, version: str) -> str:
        return f"{pipeline_id}:{version}"

    def seed(self, pipeline_version: PipelineVersion, graph: DependencyGraph):
        key = self._key(pipeline_version.pipeline_id, pipeline_version.version)
        self._versions[key] = pipeline_version
        self._graphs[key] = graph

    def get_pipeline_version(self, pipeline_id: str, version: str) -> Optional[PipelineVersion]:
        return self._versions.get(self._key(pipeline_id, version))

    def get_dependency_graph(self, pipeline_id: str, version: str) -> Optional[DependencyGraph]:
        return self._graphs.get(self._key(pipeline_id, version))
