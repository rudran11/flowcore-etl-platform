from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ScheduleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ScheduleType(str, Enum):
    CRON = "CRON"
    INTERVAL = "INTERVAL"
    ONE_TIME = "ONE_TIME"
    MANUAL = "MANUAL"
    EVENT = "EVENT"

class ScheduleBase(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_id: str
    pipeline_id: str
    type: ScheduleType
    expression: Optional[str] = None  # e.g., cron string, or interval seconds
    timezone: str = "UTC"
    max_retries: int = 0
    retry_delay_seconds: int = 300
    holiday_calendar: Optional[str] = None # e.g. 'US', 'UK'
    blackout_windows: Optional[list] = None # List of time ranges

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ScheduleType] = None
    expression: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[ScheduleStatus] = None

class Schedule(ScheduleBase):
    id: str
    status: ScheduleStatus
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ScheduleRunHistory(BaseModel):
    id: str
    schedule_id: str
    execution_id: str
    triggered_at: datetime
    status: str  # maps to execution status
    
    class Config:
        from_attributes = True

class SchedulerMetrics(BaseModel):
    queue_length: int
    avg_execution_delay_seconds: float
    success_rate: float
    failure_rate: float
    last_heartbeat: datetime
    missed_schedules: int
