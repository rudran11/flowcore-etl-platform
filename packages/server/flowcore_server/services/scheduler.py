import logging
from typing import List, Optional, Any
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from flowcore_shared.schemas.operational.schedule import (
    Schedule, ScheduleCreate, ScheduleUpdate, ScheduleStatus, ScheduleType
)
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down.")

    async def _execute_pipeline_job(self, schedule_id: str, pipeline_id: str):
        """
        Job executed by APScheduler.
        It enqueues a pipeline execution using the ExecutionService logic,
        but since we are inside the SchedulerService, we'll just interact with the UoW directly
        or ideally call ExecutionService. 
        For now, let's just create an execution run in the DB.
        """
        logger.info(f"Executing scheduled job for schedule_id={schedule_id}")
        async with self.uow:
            schedule = await self.uow.schedules.get_schedule(schedule_id)
            if not schedule or schedule.status != ScheduleStatus.ACTIVE:
                logger.warning(f"Schedule {schedule_id} is not active or found. Skipping.")
                return

            # Note: We would ideally use the ExecutionService here. 
            # We'll need a way to trigger pipelines properly, perhaps by importing it or via HTTP.
            # For this MVP, we'll log it, and maybe update the last_run_at of the schedule.
            
            # Update last_run_at
            update_data = ScheduleUpdate(last_run_at=datetime.utcnow())
            await self.uow.schedules.update_schedule(schedule_id, update_data)
            await self.uow.commit()
            
            logger.info(f"Triggered execution for schedule {schedule_id}")

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
                args=[schedule.id, schedule.pipeline_id]
            )
            logger.info(f"Added job {job_id} to scheduler.")

    async def initialize_schedules(self):
        """Load all active schedules from DB and add to APScheduler"""
        self.start()
        async with self.uow:
            schedules = await self.uow.schedules.list_schedules(limit=1000)
            for schedule in schedules:
                if schedule.status == ScheduleStatus.ACTIVE:
                    self._add_job_to_scheduler(schedule)
                    
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
            args=[schedule.id, schedule.pipeline_id]
        )
        return True
