from abc import ABC, abstractmethod
from typing import List, Optional
from flowcore_shared.schemas.operational.schedule import Schedule, ScheduleCreate, ScheduleUpdate

class AbstractScheduleRepository(ABC):
    @abstractmethod
    async def create_schedule(self, schedule: ScheduleCreate) -> Schedule:
        pass

    @abstractmethod
    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        pass

    @abstractmethod
    async def list_schedules(self, skip: int = 0, limit: int = 100, pipeline_id: Optional[str] = None) -> List[Schedule]:
        pass

    @abstractmethod
    async def update_schedule(self, schedule_id: str, schedule: ScheduleUpdate) -> Optional[Schedule]:
        pass

    @abstractmethod
    async def delete_schedule(self, schedule_id: str) -> bool:
        pass
