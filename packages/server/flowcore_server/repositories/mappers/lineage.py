from typing import List
from flowcore_shared.schemas.lineage.dataset import Dataset, DatasetType
from flowcore_shared.schemas.lineage.graph import LineageEdge, ConfidenceLevel
from flowcore_server.db.lineage_models import Dataset as OrmDataset, LineageEdge as OrmLineageEdge
import uuid

def map_orm_to_dataset(orm_obj: OrmDataset) -> Dataset:
    return Dataset(
        id=str(orm_obj.id),
        workspace_id=str(orm_obj.workspace_id),
        environment_id=str(orm_obj.environment_id) if orm_obj.environment_id else None,
        name=orm_obj.name,
        type=DatasetType(orm_obj.type),
        description=orm_obj.description,
        owner=orm_obj.owner,
        version=orm_obj.version,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )

def map_orm_to_lineage_edge(orm_obj: OrmLineageEdge) -> LineageEdge:
    return LineageEdge(
        id=str(orm_obj.id),
        upstream_id=str(orm_obj.upstream_id),
        downstream_id=str(orm_obj.downstream_id),
        pipeline_id=str(orm_obj.pipeline_id) if orm_obj.pipeline_id else None,
        execution_id=str(orm_obj.execution_id) if orm_obj.execution_id else None,
        confidence_level=ConfidenceLevel(orm_obj.confidence_level),
        created_at=orm_obj.created_at
    )
