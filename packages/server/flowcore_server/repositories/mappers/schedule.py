from flowcore_shared.schemas.operational.schedule import Schedule, ScheduleStatus, ScheduleType
from flowcore_server.db.models import Schedule as OrmSchedule
from datetime import datetime

def map_orm_to_schedule(orm_obj: OrmSchedule) -> Schedule:
    return Schedule(
        id=str(orm_obj.id),
        workspace_id=str(orm_obj.workspace_id) if orm_obj.workspace_id else "",
        name=orm_obj.name,
        description=orm_obj.description,
        pipeline_id=str(orm_obj.pipeline_id),
        type=ScheduleType(orm_obj.type),
        expression=orm_obj.expression,
        timezone=orm_obj.timezone,
        status=ScheduleStatus(orm_obj.status),
        next_run_at=orm_obj.next_run_at,
        last_run_at=orm_obj.last_run_at,
        # assuming Base adds created_at and updated_at, if not we'll use datetime.utcnow()
        created_at=getattr(orm_obj, "created_at", datetime.utcnow()),
        updated_at=getattr(orm_obj, "updated_at", datetime.utcnow())
    )

def map_schedule_to_orm(schedule: Schedule) -> OrmSchedule:
    return OrmSchedule(
        id=schedule.id,
        workspace_id=schedule.workspace_id,
        name=schedule.name,
        description=schedule.description,
        pipeline_id=schedule.pipeline_id,
        type=schedule.type.value,
        expression=schedule.expression,
        timezone=schedule.timezone,
        status=schedule.status.value,
        next_run_at=schedule.next_run_at,
        last_run_at=schedule.last_run_at
    )
