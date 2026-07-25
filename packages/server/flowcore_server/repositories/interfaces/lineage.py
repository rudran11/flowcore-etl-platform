from abc import ABC, abstractmethod
from typing import List, Optional
from flowcore_shared.schemas.lineage.dataset import Dataset, DatasetCreate, DatasetUpdate
from flowcore_shared.schemas.lineage.column import DatasetColumn, DatasetColumnCreate
from flowcore_shared.schemas.lineage.graph import LineageEdge, LineageEdgeCreate

class AbstractLineageRepository(ABC):
    @abstractmethod
    async def create_dataset(self, workspace_id: str, data: DatasetCreate) -> Dataset:
        pass

    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        pass

    @abstractmethod
    async def update_dataset(self, dataset_id: str, data: DatasetUpdate) -> Dataset:
        pass

    @abstractmethod
    async def list_datasets(self, workspace_id: str) -> List[Dataset]:
        pass

    @abstractmethod
    async def delete_dataset(self, dataset_id: str) -> None:
        pass

    @abstractmethod
    async def create_edge(self, edge: LineageEdgeCreate) -> LineageEdge:
        pass

    @abstractmethod
    async def get_upstream(self, dataset_id: str) -> List[LineageEdge]:
        pass

    @abstractmethod
    async def get_downstream(self, dataset_id: str) -> List[LineageEdge]:
        pass
