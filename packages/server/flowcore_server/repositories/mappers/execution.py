from flowcore.models.operational.execution import ExecutionRun as DomainExecutionRun, ExecutionStepRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.db.models import ExecutionRun as OrmExecutionRun, ExecutionStep as OrmExecutionStep
import uuid

def map_orm_to_execution_run(orm_obj: OrmExecutionRun) -> DomainExecutionRun:
    steps = {}
    if orm_obj.steps:
        for step in orm_obj.steps:
            steps[step.step_id] = ExecutionStepRun(
                id=str(step.id),
                step_id=step.step_id,
                status=ExecutionState(step.status),
                start_time=step.started_at,
                end_time=step.completed_at,
                retry_count=step.retry_count,
                error_message=step.error_message,
                outputs=step.outputs or {},
                logs=step.logs or [],
                created_at=step.created_at,
                updated_at=step.updated_at
            )

    return DomainExecutionRun(
        id=str(orm_obj.id),
        workspace_id=str(orm_obj.workspace_id) if orm_obj.workspace_id else "",
        pipeline_id=str(orm_obj.pipeline_version.pipeline_id) if getattr(orm_obj, "pipeline_version", None) else "",
        pipeline_version_id=str(orm_obj.pipeline_version_id),
        status=ExecutionState(orm_obj.status),
        trigger_type=orm_obj.parameters.get("trigger_type", "MANUAL"),
        start_time=orm_obj.started_at,
        end_time=orm_obj.completed_at,
        error_message=orm_obj.error_message,
        outputs=orm_obj.outputs or {},
        steps=steps,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )

def map_execution_run_to_orm(domain_obj: DomainExecutionRun) -> OrmExecutionRun:
    orm_run = OrmExecutionRun(
        id=uuid.UUID(domain_obj.id),
        workspace_id=uuid.UUID(domain_obj.workspace_id) if domain_obj.workspace_id else None,
        pipeline_version_id=uuid.UUID(domain_obj.pipeline_version_id),
        status=domain_obj.status.value,
        parameters={"trigger_type": domain_obj.trigger_type},
        started_at=domain_obj.start_time,
        completed_at=domain_obj.end_time,
        error_message=domain_obj.error_message,
        outputs=domain_obj.outputs,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at
    )
    
    orm_steps = []
    for step_id, step in domain_obj.steps.items():
        orm_steps.append(OrmExecutionStep(
            id=uuid.UUID(step.id),
            run_id=orm_run.id,
            step_id=step.step_id,
            status=step.status.value,
            started_at=step.start_time,
            completed_at=step.end_time,
            retry_count=step.retry_count,
            error_message=step.error_message,
            outputs=step.outputs,
            logs=step.logs,
            created_at=step.created_at,
            updated_at=step.updated_at
        ))
    
    orm_run.steps = orm_steps
    return orm_run
