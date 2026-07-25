import uuid
from typing import List, Optional
from flowcore_server.repositories.interfaces.lineage import AbstractLineageRepository
from flowcore_shared.schemas.lineage.dataset import Dataset, DatasetCreate, DatasetUpdate
from flowcore_shared.schemas.lineage.graph import LineageEdge, LineageEdgeCreate

class InMemoryLineageRepository(AbstractLineageRepository):
    def __init__(self):
        self.datasets: dict[str, Dataset] = {}
        self.edges: dict[str, LineageEdge] = {}

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        return self.datasets.get(dataset_id)

    async def get_dataset_by_name(self, workspace_id: str, name: str) -> Optional[Dataset]:
        for ds in self.datasets.values():
            if ds.workspace_id == workspace_id and ds.name == name:
                return ds
        return None

    async def create_dataset(self, workspace_id: str, dataset: DatasetCreate) -> Dataset:
        existing = await self.get_dataset_by_name(workspace_id, dataset.name)
        if existing:
            return existing
            
        ds_id = str(uuid.uuid4())
        ds = Dataset(
            id=ds_id,
            workspace_id=workspace_id,
            name=dataset.name,
            type=dataset.type,
            description=dataset.description,
            owner=dataset.owner,
            version=1,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z"
        )
        self.datasets[ds_id] = ds
        return ds

    async def update_dataset(self, dataset_id: str, dataset: DatasetUpdate) -> Dataset:
        ds = self.datasets.get(dataset_id)
        if not ds:
            raise ValueError("Not found")
        if dataset.description is not None:
            ds.description = dataset.description
        if dataset.owner is not None:
            ds.owner = dataset.owner
        return ds

    async def list_datasets(self, workspace_id: str) -> List[Dataset]:
        return [ds for ds in self.datasets.values() if ds.workspace_id == workspace_id]

    async def delete_dataset(self, dataset_id: str) -> None:
        if dataset_id in self.datasets:
            del self.datasets[dataset_id]

    async def create_edge(self, edge: LineageEdgeCreate) -> LineageEdge:
        edge_id = str(uuid.uuid4())
        le = LineageEdge(
            id=edge_id,
            upstream_id=edge.upstream_id,
            downstream_id=edge.downstream_id,
            pipeline_id=edge.pipeline_id,
            execution_id=edge.execution_id,
            confidence_level=edge.confidence_level,
            created_at="2026-01-01T00:00:00Z"
        )
        self.edges[edge_id] = le
        return le

    async def get_upstream(self, dataset_id: str) -> List[LineageEdge]:
        return [e for e in self.edges.values() if e.downstream_id == dataset_id]

    async def get_downstream(self, dataset_id: str) -> List[LineageEdge]:
        return [e for e in self.edges.values() if e.upstream_id == dataset_id]
