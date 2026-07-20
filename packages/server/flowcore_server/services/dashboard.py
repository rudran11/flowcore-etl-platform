from typing import Dict, Any
from datetime import datetime
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.models.dashboard import (
    DashboardResponse,
    DashboardStatistics,
    ExecutionSummary,
    ExecutionTrend,
    SystemHealth
)

class DashboardService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get_dashboard(self) -> DashboardResponse:
        async with self.uow:
            # 1. Pipeline count
            total_pipelines = await self.uow.pipelines.count_pipelines()
            
            # 2. Execution counts & summary
            # We want to minimize queries.
            # execution_summary() gives counts by state
            summary_dict = await self.uow.executions.execution_summary()
            
            completed = summary_dict.get("completed", 0)
            failed = summary_dict.get("failed", 0)
            running = summary_dict.get("running", 0)
            cancelled = summary_dict.get("cancelled", 0)
            queued = summary_dict.get("queued", 0)
            
            total_runs = sum(summary_dict.values())
            
            terminal_runs = completed + failed + cancelled
            success_rate = (completed / terminal_runs * 100) if terminal_runs > 0 else 0.0
            
            avg_duration_ms = await self.uow.executions.average_duration_ms()
            
            # 3. Trends
            daily_counts = await self.uow.executions.daily_execution_counts(days=7)
            trends = [ExecutionTrend(**day) for day in daily_counts]
            
            # 4. Recent runs
            recent = await self.uow.executions.recent_runs(limit=10)
            
            # 5. System Health
            health = SystemHealth(
                server="healthy",
                database="healthy", # Assuming healthy if we got this far
                engine="unknown", # We can extend this later
                api="v1",
                version="1.0.0"
            )
            
            return DashboardResponse(
                statistics=DashboardStatistics(
                    total_pipelines=total_pipelines,
                    total_runs=total_runs,
                    success_rate=round(success_rate, 2),
                    avg_duration_ms=round(avg_duration_ms, 2)
                ),
                execution_summary=ExecutionSummary(
                    completed=completed,
                    failed=failed,
                    running=running,
                    cancelled=cancelled,
                    queued=queued
                ),
                trends=trends,
                recent_runs=recent,
                health=health,
                generated_at=datetime.utcnow()
            )
