import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from flowcore_shared.schemas.operational.schedule import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleStatus
from flowcore_server.db.models import Schedule as OrmSchedule
from flowcore_server.repositories.interfaces.schedule import AbstractScheduleRepository
from flowcore_server.repositories.mappers.schedule import map_orm_to_schedule, map_schedule_to_orm
from datetime import datetime

class PostgresScheduleRepository(AbstractScheduleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_schedule(self, schedule_data: ScheduleCreate) -> Schedule:
        schedule_id = str(uuid.uuid4())
        orm_obj = OrmSchedule(
            id=schedule_id,
            name=schedule_data.name,
            description=schedule_data.description,
            pipeline_id=schedule_data.pipeline_id,
            type=schedule_data.type.value,
            expression=schedule_data.expression,
            timezone=schedule_data.timezone,
            status=ScheduleStatus.ACTIVE.value
        )
        self.session.add(orm_obj)
        await self.session.flush()
        return map_orm_to_schedule(orm_obj)

    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        stmt = select(OrmSchedule).where(OrmSchedule.id == schedule_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_schedule(orm_obj)
        return None

    async def list_schedules(self, skip: int = 0, limit: int = 100, pipeline_id: Optional[str] = None) -> List[Schedule]:
        stmt = select(OrmSchedule)
        if pipeline_id:
            stmt = stmt.where(OrmSchedule.pipeline_id == pipeline_id)
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        return [map_orm_to_schedule(obj) for obj in orm_objs]

    async def update_schedule(self, schedule_id: str, schedule: ScheduleUpdate) -> Optional[Schedule]:
        stmt = select(OrmSchedule).where(OrmSchedule.id == schedule_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        
        if not orm_obj:
            return None
            
        update_data = schedule.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(orm_obj, key):
                if hasattr(value, "value"): # Handle enums
                    setattr(orm_obj, key, value.value)
                else:
                    setattr(orm_obj, key, value)
                    
        await self.session.flush()
        return map_orm_to_schedule(orm_obj)

    async def delete_schedule(self, schedule_id: str) -> bool:
        stmt = select(OrmSchedule).where(OrmSchedule.id == schedule_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            await self.session.delete(orm_obj)
            await self.session.flush()
            return True
        return False
