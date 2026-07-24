from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from flowcore_server.models.schedule import Schedule, ScheduleCreate, ScheduleUpdate, SchedulerMetrics
from flowcore_server.services.scheduler import SchedulerService
from flowcore_server.repositories.factory import RepositoryFactory
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.auth import require_permissions, UserInDB

router = APIRouter(prefix="/schedules", tags=["Schedules"])

def get_uow() -> AbstractUnitOfWork:
    factory = RepositoryFactory(use_postgres=True)
    return factory.get_unit_of_work()

def get_scheduler_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> SchedulerService:
    # Normally this would be a singleton, but for this MVP we'll instantiate it here.
    # It will use the same APScheduler instance under the hood if it's singleton-like,
    # but AsyncIOScheduler instances are independent.
    # We should have initialized this at app startup, but this will do for basic CRUD.
    return SchedulerService(uow)

@router.get("/metrics", response_model=SchedulerMetrics, summary="Get scheduler metrics")
async def get_metrics(
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions([]))
):
    # Mock metrics for now, as we don't have historical data or queue systems implemented yet
    from datetime import datetime
    return SchedulerMetrics(
        queue_length=12,
        avg_execution_delay_seconds=1.4,
        success_rate=0.98,
        failure_rate=0.02,
        last_heartbeat=datetime.utcnow(),
        missed_schedules=0
    )

@router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_in: ScheduleCreate,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions(["schedule:create"]))
):
    return await service.create_schedule(schedule_in)

@router.get("", response_model=List[Schedule])
async def list_schedules(
    skip: int = 0,
    limit: int = 100,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions([]))
):
    return await service.list_schedules(skip=skip, limit=limit)

@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions([]))
):
    schedule = await service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: str,
    schedule_in: ScheduleUpdate,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions(["schedule:update"]))
):
    schedule = await service.update_schedule(schedule_id, schedule_in)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions(["schedule:update"]))
):
    success = await service.delete_schedule(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")

@router.post("/{schedule_id}/pause", response_model=Schedule)
async def pause_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions(["schedule:update"]))
):
    schedule = await service.pause_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/{schedule_id}/resume", response_model=Schedule)
async def resume_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions(["schedule:update"]))
):
    schedule = await service.resume_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.post("/{schedule_id}/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service),
    user: UserInDB = Depends(require_permissions(["schedule:update"]))
):
    success = await service.trigger_now(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Job triggered successfully"}
