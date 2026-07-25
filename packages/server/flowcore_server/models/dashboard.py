from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from flowcore.models.operational.execution import ExecutionRun

class ExecutionSummary(BaseModel):
    completed: int = 0
    failed: int = 0
    running: int = 0
    cancelled: int = 0
    queued: int = 0

class ExecutionTrend(BaseModel):
    date: str
    completed: int = 0
    failed: int = 0
    running: int = 0
    cancelled: int = 0
    queued: int = 0

class DashboardStatistics(BaseModel):
    total_pipelines: int
    total_runs: int
    success_rate: float
    avg_duration_ms: float

class SystemHealth(BaseModel):
    server: str
    database: str
    engine: str
    api: str
    version: str

class DashboardResponse(BaseModel):
    statistics: DashboardStatistics
    execution_summary: ExecutionSummary
    trends: List[ExecutionTrend]
    recent_runs: List[ExecutionRun]
    health: SystemHealth
    generated_at: datetime
