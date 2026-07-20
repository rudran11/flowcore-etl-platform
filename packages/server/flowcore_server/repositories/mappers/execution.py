from flowcore_shared.schemas.operational.execution import ExecutionRun as DomainExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.db.models import ExecutionRun as OrmExecutionRun
import uuid

def map_orm_to_execution_run(orm_obj: OrmExecutionRun) -> DomainExecutionRun:
    return DomainExecutionRun(
        id=str(orm_obj.id),
        # pipeline_id is technically available via orm_obj.pipeline_version.pipeline_id but 
        # for mapper simplicity we can pass it if we eagerly load, or default it.
        # Since our schema requires pipeline_id, we extract it.
        pipeline_id=str(orm_obj.pipeline_version.pipeline_id) if orm_obj.pipeline_version else "",
        pipeline_version_id=str(orm_obj.pipeline_version_id),
        status=ExecutionState(orm_obj.status),
        trigger_type=orm_obj.parameters.get("trigger_type", "MANUAL"),
        start_time=orm_obj.started_at,
        end_time=orm_obj.completed_at,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )

def map_execution_run_to_orm(domain_obj: DomainExecutionRun) -> OrmExecutionRun:
    return OrmExecutionRun(
        id=uuid.UUID(domain_obj.id),
        pipeline_version_id=uuid.UUID(domain_obj.pipeline_version_id),
        status=domain_obj.status.value,
        parameters={"trigger_type": domain_obj.trigger_type},
        started_at=domain_obj.start_time,
        completed_at=domain_obj.end_time,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at
    )
