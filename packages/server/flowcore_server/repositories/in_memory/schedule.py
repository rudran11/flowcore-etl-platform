from typing import List, Optional, Dict
from flowcore_server.repositories.interfaces.schedule import AbstractScheduleRepository
from flowcore_shared.schemas.operational.schedule import Schedule, ScheduleCreate, ScheduleUpdate
import uuid
from datetime import datetime, timezone

class InMemoryScheduleRepository(AbstractScheduleRepository):
    def __init__(self):
        self._store: Dict[str, Schedule] = {}

    async def create_schedule(self, schedule: ScheduleCreate) -> Schedule:
        schedule_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        new_schedule = Schedule(
            id=schedule_id,
            created_at=now,
            updated_at=now,
            **schedule.model_dump()
        )
        self._store[schedule_id] = new_schedule
        return new_schedule

    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        return self._store.get(schedule_id)

    async def list_schedules(self, skip: int = 0, limit: int = 100, pipeline_id: Optional[str] = None) -> List[Schedule]:
        schedules = list(self._store.values())
        if pipeline_id:
            schedules = [s for s in schedules if s.pipeline_id == pipeline_id]
        return schedules[skip: skip + limit]

    async def update_schedule(self, schedule_id: str, schedule: ScheduleUpdate) -> Optional[Schedule]:
        if schedule_id not in self._store:
            return None
        existing = self._store[schedule_id]
        update_data = schedule.model_dump(exclude_unset=True)
        updated = existing.model_copy(update=update_data)
        updated.updated_at = datetime.now(timezone.utc)
        self._store[schedule_id] = updated
        return updated

    async def delete_schedule(self, schedule_id: str) -> bool:
        if schedule_id in self._store:
            del self._store[schedule_id]
            return True
        return False
        
    async def create_run_history(self, history):
        pass
        
    async def update_last_run_at(self, schedule_id: str, last_run_at: datetime):
        if schedule_id in self._store:
            existing = self._store[schedule_id]
            updated = existing.model_copy(update={"last_run_at": last_run_at})
            self._store[schedule_id] = updated
