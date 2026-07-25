from typing import List, Optional
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from flowcore_shared.schemas.lineage.dataset import Dataset, DatasetCreate, DatasetUpdate
from flowcore_shared.schemas.lineage.graph import LineageEdge, LineageEdgeCreate
from flowcore_server.db.lineage_models import Dataset as OrmDataset, LineageEdge as OrmLineageEdge
from flowcore_server.repositories.interfaces.lineage import AbstractLineageRepository
from flowcore_server.repositories.mappers.lineage import map_orm_to_dataset, map_orm_to_lineage_edge

class AsyncSqlAlchemyLineageRepository(AbstractLineageRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(self, workspace_id: str, data: DatasetCreate) -> Dataset:
        orm_dataset = OrmDataset(
            id=uuid.uuid4(),
            workspace_id=uuid.UUID(workspace_id),
            name=data.name,
            type=data.type.value,
            description=data.description,
            owner=data.owner
        )
        self.session.add(orm_dataset)
        await self.session.flush()
        return map_orm_to_dataset(orm_dataset)

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        stmt = select(OrmDataset).where(OrmDataset.id == uuid.UUID(dataset_id))
        result = await self.session.execute(stmt)
        orm_dataset = result.scalars().first()
        if orm_dataset:
            return map_orm_to_dataset(orm_dataset)
        return None

    async def update_dataset(self, dataset_id: str, data: DatasetUpdate) -> Dataset:
        stmt = select(OrmDataset).where(OrmDataset.id == uuid.UUID(dataset_id))
        result = await self.session.execute(stmt)
        orm_dataset = result.scalars().first()
        if orm_dataset:
            if data.name is not None:
                orm_dataset.name = data.name
            if data.type is not None:
                orm_dataset.type = data.type.value
            if data.description is not None:
                orm_dataset.description = data.description
            if data.owner is not None:
                orm_dataset.owner = data.owner
            await self.session.flush()
            return map_orm_to_dataset(orm_dataset)
        raise ValueError("Dataset not found")

    async def list_datasets(self, workspace_id: str) -> List[Dataset]:
        stmt = select(OrmDataset).where(OrmDataset.workspace_id == uuid.UUID(workspace_id)).order_by(OrmDataset.name)
        result = await self.session.execute(stmt)
        return [map_orm_to_dataset(d) for d in result.scalars().all()]

    async def delete_dataset(self, dataset_id: str) -> None:
        stmt = delete(OrmDataset).where(OrmDataset.id == uuid.UUID(dataset_id))
        await self.session.execute(stmt)
        await self.session.flush()

    async def create_edge(self, edge: LineageEdgeCreate) -> LineageEdge:
        orm_edge = OrmLineageEdge(
            id=uuid.uuid4(),
            upstream_id=uuid.UUID(edge.upstream_id),
            downstream_id=uuid.UUID(edge.downstream_id),
            pipeline_id=uuid.UUID(edge.pipeline_id) if edge.pipeline_id else None,
            execution_id=uuid.UUID(edge.execution_id) if edge.execution_id else None,
            confidence_level=edge.confidence_level.value
        )
        self.session.add(orm_edge)
        await self.session.flush()
        return map_orm_to_lineage_edge(orm_edge)

    async def get_upstream(self, dataset_id: str) -> List[LineageEdge]:
        stmt = select(OrmLineageEdge).where(OrmLineageEdge.downstream_id == uuid.UUID(dataset_id))
        result = await self.session.execute(stmt)
        return [map_orm_to_lineage_edge(e) for e in result.scalars().all()]

    async def get_downstream(self, dataset_id: str) -> List[LineageEdge]:
        stmt = select(OrmLineageEdge).where(OrmLineageEdge.upstream_id == uuid.UUID(dataset_id))
        result = await self.session.execute(stmt)
        return [map_orm_to_lineage_edge(e) for e in result.scalars().all()]
