from flowcore_shared.schemas.pipeline import Pipeline as DomainPipeline
from flowcore_shared.schemas.pipeline import PipelineVersion as DomainPipelineVersion
from flowcore_shared.schemas.pipeline import ExecutionStep as DomainExecutionStep
from flowcore_server.db.models import Pipeline as OrmPipeline
from flowcore_server.db.models import PipelineVersion as OrmPipelineVersion
from flowcore_server.db.models import ExecutionStep as OrmExecutionStep
import uuid

def map_orm_to_pipeline(orm_obj: OrmPipeline) -> DomainPipeline:
    return DomainPipeline(
        id=str(orm_obj.id),
        name=orm_obj.name,
        owner=orm_obj.owner,
        description=orm_obj.description,
        tags=orm_obj.tags,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )

def map_pipeline_to_orm(domain_obj: DomainPipeline) -> OrmPipeline:
    return OrmPipeline(
        id=uuid.UUID(domain_obj.id),
        name=domain_obj.name,
        owner=domain_obj.owner,
        description=domain_obj.description,
        tags=domain_obj.tags,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at
    )

def map_orm_to_pipeline_version(orm_obj: OrmPipelineVersion) -> DomainPipelineVersion:
    # We rebuild the DomainPipelineVersion from the stored dsl/graph definitions and steps
    return DomainPipelineVersion(
        id=str(orm_obj.id),
        pipeline_id=str(orm_obj.pipeline_id),
        version=orm_obj.version_tag,
        steps=[], # Populated if needed
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )
