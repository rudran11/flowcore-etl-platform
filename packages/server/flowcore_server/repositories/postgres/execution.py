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

    async def execution_summary(self) -> dict:
        from sqlalchemy import func
        stmt = select(OrmExecutionRun.status, func.count(OrmExecutionRun.id)).group_by(OrmExecutionRun.status)
        result = await self.session.execute(stmt)
        summary = {state.value: 0 for state in ExecutionState}
        for status, count in result.all():
            if status in summary:
                summary[status] = count
        return summary

    async def daily_execution_counts(self, days: int = 7) -> List[dict]:
        from sqlalchemy import func, Date, cast
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days-1)
        day_expr = cast(OrmExecutionRun.started_at, Date)
        
        stmt = (
            select(day_expr, OrmExecutionRun.status, func.count(OrmExecutionRun.id))
            .where(OrmExecutionRun.started_at >= start_date)
            .group_by(day_expr, OrmExecutionRun.status)
        )
        result = await self.session.execute(stmt)
        
        date_counts = {}
        for row in result.all():
            date_obj, status, count = row
            if date_obj is None:
                continue
            date_str = date_obj.strftime("%Y-%m-%d") if hasattr(date_obj, 'strftime') else str(date_obj)
            if date_str not in date_counts:
                date_counts[date_str] = {state.value: 0 for state in ExecutionState}
            if status in date_counts[date_str]:
                date_counts[date_str][status] = count
                
        res = []
        now = datetime.utcnow()
        for i in range(days):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            day_dict = {"date": d}
            if d in date_counts:
                day_dict.update(date_counts[d])
            else:
                day_dict.update({state.value: 0 for state in ExecutionState})
            res.append(day_dict)
            
        return res[::-1]

    async def average_duration_ms(self) -> float:
        from sqlalchemy import func
        stmt = select(func.avg(
            func.extract('epoch', OrmExecutionRun.completed_at) - 
            func.extract('epoch', OrmExecutionRun.started_at)
        )).where(OrmExecutionRun.status == ExecutionState.COMPLETED.value)
        result = await self.session.execute(stmt)
        avg_sec = result.scalar_one_or_none()
        if avg_sec is not None:
            return float(avg_sec) * 1000
        return 0.0

    async def recent_runs(self, limit: int = 10, offset: int = 0) -> List[ExecutionRun]:
        stmt = (
            select(OrmExecutionRun)
            .options(selectinload(OrmExecutionRun.pipeline_version))
            .order_by(OrmExecutionRun.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [map_orm_to_execution_run(obj) for obj in result.scalars().all()]
