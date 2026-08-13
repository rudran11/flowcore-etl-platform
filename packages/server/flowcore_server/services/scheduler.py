import logging
from typing import List, Optional, Any
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from flowcore_shared.schemas.operational.schedule import (
    Schedule, ScheduleCreate, ScheduleUpdate, ScheduleStatus, ScheduleType
)
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork

from flowcore_server.dependencies.context import workspace_context

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, uow: AbstractUnitOfWork, execution_service: Optional[Any] = None):
        self.uow = uow
        self.execution_service = execution_service
        self.scheduler = AsyncIOScheduler(
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 300
            }
        )
        
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down.")

    async def _execute_pipeline_job(self, schedule_id: str, pipeline_id: str, workspace_id: str, manual: bool = False):
        """
        Job executed by APScheduler.
        It enqueues a pipeline execution using the ExecutionService.
        """
        logger.info(f"Executing scheduled job for schedule_id={schedule_id} in workspace {workspace_id}")
        
        token = workspace_context.set(str(workspace_id))
        try:
            async with self.uow:
                schedule = await self.uow.schedules.get_schedule(schedule_id)
                if not schedule:
                    logger.warning(f"Schedule {schedule_id} not found. Skipping.")
                    return
                if schedule.status != ScheduleStatus.ACTIVE and not manual:
                    logger.warning(f"Schedule {schedule_id} is not active. Skipping.")
                    return

                if not self.execution_service:
                    logger.error("ExecutionService not injected into SchedulerService!")
                    return
                
                pipeline = await self.uow.pipelines.get_pipeline(pipeline_id)
                if not pipeline:
                    logger.error(f"Pipeline {pipeline_id} not found. Skipping execution.")
                    return
                    
                versions = await self.uow.pipelines.list_pipeline_versions(pipeline_id)
                if not versions:
                    logger.error(f"No versions found for pipeline {pipeline_id}. Skipping execution.")
                    return
            
            trigger_type = "MANUAL" if manual else "SCHEDULED"
            run = await self.execution_service.start_execution(
                pipeline_id=pipeline_id,
                version=versions[0].version,
                trigger_type=trigger_type,
                parameters={"schedule_id": schedule_id}
            )
            
            async with self.uow:
                await self.uow.schedules.create_run_history(
                    schedule_id=schedule_id,
                    execution_id=run.id,
                    status=run.status.value
                )
                
                await self.uow.schedules.update_last_run_at(schedule_id, datetime.now(timezone.utc))
                await self.uow.commit()
                
                logger.info(f"Triggered execution {run.id} for schedule {schedule_id}")
        except Exception as e:
            logger.error(f"Error executing scheduled job {schedule_id}: {str(e)}", exc_info=True)
        finally:
            workspace_context.reset(token)

    def _add_job_to_scheduler(self, schedule: Schedule):
        """Add a job to APScheduler based on Schedule entity"""
        job_id = schedule.id
        
        # Remove if exists to avoid duplicates
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            
        if schedule.status != ScheduleStatus.ACTIVE:
            return

        trigger: Any = None
        if schedule.type == ScheduleType.CRON and schedule.expression:
            try:
                # Basic cron parsing (minute hour day month day_of_week)
                parts = schedule.expression.split()
                if len(parts) == 5:
                    trigger = CronTrigger(
                        minute=parts[0], hour=parts[1], day=parts[2], month=parts[3], day_of_week=parts[4],
                        timezone=schedule.timezone
                    )
            except Exception as e:
                logger.error(f"Failed to parse cron trigger for schedule {schedule.id}: {e}")
                return
        elif schedule.type == ScheduleType.INTERVAL and schedule.expression:
            try:
                seconds = int(schedule.expression)
                trigger = IntervalTrigger(seconds=seconds, timezone=schedule.timezone)
            except Exception:
                logger.error(f"Failed to parse interval trigger for schedule {schedule.id}")
                return
        elif schedule.type == ScheduleType.ONE_TIME and schedule.expression:
            try:
                run_date = datetime.fromisoformat(schedule.expression.replace("Z", "+00:00"))
                trigger = DateTrigger(run_date=run_date, timezone=schedule.timezone)
            except Exception:
                logger.error(f"Failed to parse date trigger for schedule {schedule.id}")
                return
                
        if trigger:
            self.scheduler.add_job(
                self._execute_pipeline_job,
                trigger=trigger,
                id=job_id,
                args=[schedule.id, schedule.pipeline_id, str(schedule.workspace_id), False]
            )
            logger.info(f"Added job {job_id} to scheduler.")

    async def initialize_schedules(self):
        """Load all active schedules from DB and add to APScheduler"""
        self.start()
        
        from sqlalchemy.future import select
        from flowcore_server.db.models import Schedule as OrmSchedule
        from flowcore_server.repositories.mappers.schedule import map_orm_to_schedule
        
        async with self.uow:
            stmt = select(OrmSchedule).where(OrmSchedule.status == ScheduleStatus.ACTIVE.value)
            result = await self.uow.session.execute(stmt)
            orm_schedules = result.scalars().all()
            
            for obj in orm_schedules:
                schedule = map_orm_to_schedule(obj)
                self._add_job_to_scheduler(schedule)
                
            logger.info(f"Initialized {len(orm_schedules)} active schedules across all workspaces.")
                    
    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        async with self.uow:
            return await self.uow.schedules.get_schedule(schedule_id)

    async def list_schedules(self, skip: int = 0, limit: int = 100) -> List[Schedule]:
        async with self.uow:
            return await self.uow.schedules.list_schedules(skip=skip, limit=limit)

    async def create_schedule(self, schedule_create: ScheduleCreate) -> Schedule:
        async with self.uow:
            schedule = await self.uow.schedules.create_schedule(schedule_create)
            await self.uow.commit()
            
            self._add_job_to_scheduler(schedule)
            return schedule

    async def update_schedule(self, schedule_id: str, schedule_update: ScheduleUpdate) -> Optional[Schedule]:
        async with self.uow:
            schedule = await self.uow.schedules.update_schedule(schedule_id, schedule_update)
            if schedule:
                await self.uow.commit()
                self._add_job_to_scheduler(schedule)
            return schedule

    async def delete_schedule(self, schedule_id: str) -> bool:
        async with self.uow:
            success = await self.uow.schedules.delete_schedule(schedule_id)
            if success:
                await self.uow.commit()
                if self.scheduler.get_job(schedule_id):
                    self.scheduler.remove_job(schedule_id)
            return success

    async def pause_schedule(self, schedule_id: str) -> Optional[Schedule]:
        update = ScheduleUpdate(status=ScheduleStatus.PAUSED)
        return await self.update_schedule(schedule_id, update)
        
    async def resume_schedule(self, schedule_id: str) -> Optional[Schedule]:
        update = ScheduleUpdate(status=ScheduleStatus.ACTIVE)
        return await self.update_schedule(schedule_id, update)
        
    async def trigger_now(self, schedule_id: str) -> bool:
        async with self.uow:
            schedule = await self.uow.schedules.get_schedule(schedule_id)
            if not schedule:
                return False
                
        # Run it asynchronously
        self.scheduler.add_job(
            self._execute_pipeline_job,
            id=f"{schedule_id}_manual_{datetime.utcnow().timestamp()}",
            args=[schedule.id, schedule.pipeline_id, str(schedule.workspace_id), True]
        )
        return True
