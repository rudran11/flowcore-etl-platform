from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import uuid
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_server.dependencies.context import get_workspace_id
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
        ws_id = uuid.UUID(get_workspace_id())
        orm_obj.workspace_id = ws_id
        for step in orm_obj.steps:
            step.workspace_id = ws_id
        self.session.add(orm_obj)
        await self.session.flush()
        
        # Load the relationship so the mapper has pipeline_id
        await self.session.refresh(orm_obj, ["pipeline_version"])
        
        return map_orm_to_execution_run(orm_obj)

    async def get_run(self, run_id: str) -> Optional[ExecutionRun]:
        stmt = (
            select(OrmExecutionRun)
            .options(selectinload(OrmExecutionRun.pipeline_version), selectinload(OrmExecutionRun.steps))
            .where(OrmExecutionRun.id == run_id, OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
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
            .where(PipelineVersion.pipeline_id == pipeline_id, OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        return [map_orm_to_execution_run(obj) for obj in orm_objs]

    async def update_run_status(self, run_id: str, status: ExecutionState) -> bool:
        stmt = select(OrmExecutionRun).where(OrmExecutionRun.id == run_id, OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
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
            stmt = select(OrmExecutionRun).options(selectinload(OrmExecutionRun.steps)).where(OrmExecutionRun.id == run.id, OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
            result = await self.session.execute(stmt)
            orm_obj = result.scalar_one()
            
            # Map updated fields
            orm_obj.status = run.status.value
            orm_obj.started_at = run.start_time
            orm_obj.completed_at = run.end_time
            orm_obj.parameters = {"trigger_type": run.trigger_type}
            orm_obj.error_message = run.error_message
            
            # Map updated steps
            from flowcore_server.db.models import ExecutionStep as OrmExecutionStep
            existing_steps = {str(step.id): step for step in orm_obj.steps}
            
            for step_id, domain_step in run.steps.items():
                if domain_step.id in existing_steps:
                    orm_step = existing_steps[domain_step.id]
                    orm_step.status = domain_step.status.value
                    orm_step.started_at = domain_step.start_time
                    orm_step.completed_at = domain_step.end_time
                    orm_step.retry_count = domain_step.retry_count
                    orm_step.error_message = domain_step.error_message
                    orm_step.outputs = domain_step.outputs
                    orm_step.logs = domain_step.logs
                else:
                    orm_step = OrmExecutionStep(
                        id=uuid.UUID(domain_step.id),
                        run_id=orm_obj.id,
                        workspace_id=orm_obj.workspace_id,
                        step_id=domain_step.step_id,
                        status=domain_step.status.value,
                        started_at=domain_step.start_time,
                        completed_at=domain_step.end_time,
                        retry_count=domain_step.retry_count,
                        error_message=domain_step.error_message,
                        outputs=domain_step.outputs,
                        logs=domain_step.logs
                    )
                    orm_obj.steps.append(orm_step)
            
            await self.session.flush()
            await self.session.refresh(orm_obj, ["pipeline_version"])
            return map_orm_to_execution_run(orm_obj)
        else:
            return await self.create_run(run)

    async def execution_summary(self) -> dict:
        from sqlalchemy import func
        stmt = select(OrmExecutionRun.status, func.count(OrmExecutionRun.id)).where(OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id())).group_by(OrmExecutionRun.status)
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
            .where(OrmExecutionRun.started_at >= start_date, OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
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
        )).where(OrmExecutionRun.status == ExecutionState.COMPLETED.value, OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        avg_sec = result.scalar_one_or_none()
        if avg_sec is not None:
            return float(avg_sec) * 1000
        return 0.0

    async def recent_runs(self, limit: int = 10, offset: int = 0) -> List[ExecutionRun]:
        stmt = (
            select(OrmExecutionRun)
            .options(selectinload(OrmExecutionRun.pipeline_version))
            .where(OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
            .order_by(OrmExecutionRun.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return [map_orm_to_execution_run(obj) for obj in result.scalars().all()]

    async def list_runs(
        self, 
        pipeline_id: Optional[str] = None, 
        status: Optional[str] = None, 
        limit: int = 25, 
        skip: int = 0
    ) -> tuple[List[ExecutionRun], int]:
        from flowcore_server.db.models import PipelineVersion
        from sqlalchemy import func
        
        base_stmt = select(OrmExecutionRun).options(selectinload(OrmExecutionRun.pipeline_version)).where(OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
        count_stmt = select(func.count(OrmExecutionRun.id)).where(OrmExecutionRun.workspace_id == uuid.UUID(get_workspace_id()))
        
        if pipeline_id:
            base_stmt = base_stmt.join(PipelineVersion, OrmExecutionRun.pipeline_version_id == PipelineVersion.id).where(PipelineVersion.pipeline_id == pipeline_id)
            count_stmt = count_stmt.join(PipelineVersion, OrmExecutionRun.pipeline_version_id == PipelineVersion.id).where(PipelineVersion.pipeline_id == pipeline_id)
            
        if status:
            base_stmt = base_stmt.where(OrmExecutionRun.status == status)
            count_stmt = count_stmt.where(OrmExecutionRun.status == status)
            
        base_stmt = base_stmt.order_by(OrmExecutionRun.created_at.desc()).limit(limit).offset(skip)
        
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one_or_none() or 0
        
        result = await self.session.execute(base_stmt)
        runs = [map_orm_to_execution_run(obj) for obj in result.scalars().all()]
        
        return runs, total
