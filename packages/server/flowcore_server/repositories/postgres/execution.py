from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.repositories.interfaces.execution import AbstractExecutionRepository
from flowcore_server.db.models import ExecutionRun as OrmExecutionRun
from flowcore_server.repositories.mappers.execution import (
    map_orm_to_execution_run, map_execution_run_to_orm
)

class PostgresExecutionRepository(AbstractExecutionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, run: ExecutionRun) -> ExecutionRun:
        orm_obj = map_execution_run_to_orm(run)
        self.session.add(orm_obj)
        await self.session.flush()
        
        # Load the relationship so the mapper has pipeline_id
        await self.session.refresh(orm_obj, ["pipeline_version"])
        
        return map_orm_to_execution_run(orm_obj)

    async def get_run(self, run_id: str) -> Optional[ExecutionRun]:
        stmt = (
            select(OrmExecutionRun)
            .options(selectinload(OrmExecutionRun.pipeline_version))
            .where(OrmExecutionRun.id == run_id)
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_execution_run(orm_obj)
        return None

    async def list_runs_for_pipeline(self, pipeline_id: str, limit: int = 100, offset: int = 0) -> List[ExecutionRun]:
        # This requires joining with PipelineVersion to filter by pipeline_id
        from flowcore_server.db.models import PipelineVersion
        stmt = (
            select(OrmExecutionRun)
            .join(PipelineVersion, OrmExecutionRun.pipeline_version_id == PipelineVersion.id)
            .options(selectinload(OrmExecutionRun.pipeline_version))
            .where(PipelineVersion.pipeline_id == pipeline_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        return [map_orm_to_execution_run(obj) for obj in orm_objs]

    async def update_run_status(self, run_id: str, status: ExecutionState) -> bool:
        stmt = select(OrmExecutionRun).where(OrmExecutionRun.id == run_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            orm_obj.status = status.value
            await self.session.flush()
            return True
        return False

    async def save(self, run: ExecutionRun) -> ExecutionRun:
        # Simplistic save for Upsert
        existing = await self.get_run(run.id)
        if existing:
            stmt = select(OrmExecutionRun).where(OrmExecutionRun.id == run.id)
            result = await self.session.execute(stmt)
            orm_obj = result.scalar_one()
            
            # Map updated fields
            orm_obj.status = run.status.value
            orm_obj.started_at = run.start_time
            orm_obj.completed_at = run.end_time
            orm_obj.parameters = {"trigger_type": run.trigger_type}
            
            await self.session.flush()
            await self.session.refresh(orm_obj, ["pipeline_version"])
            return map_orm_to_execution_run(orm_obj)
        else:
            return await self.create_run(run)
