from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ExecutionRequest(BaseModel):
    """
    DTO for initiating a pipeline execution run.
    """
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Runtime parameters to inject into the execution context.")
    timeout_seconds: Optional[int] = Field(None, description="Optional overarching timeout for the entire run.")

class ExecutionStepResponse(BaseModel):
    step_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    outputs: Dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)

class ExecutionResponse(BaseModel):
    """
    DTO for returning the status and results of an execution run.
    """
    run_id: str = Field(..., description="Unique identifier for the execution run.")
    pipeline_id: str = Field(..., description="ID of the pipeline being executed.")
    pipeline_version: str = Field(..., description="Version of the pipeline being executed.")
    status: str = Field(..., description="Current status of the execution (e.g. PENDING, RUNNING, COMPLETED, FAILED).")
    submitted_at: datetime = Field(..., description="Timestamp when the execution request was submitted.")
    started_at: Optional[datetime] = Field(None, description="Timestamp when execution started.")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when execution finished.")
    duration_ms: Optional[int] = Field(None, description="Total execution duration in milliseconds.")
    error: Optional[str] = Field(None, description="Error message if the execution failed.")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs collected from the execution steps.")
    steps: Dict[str, ExecutionStepResponse] = Field(default_factory=dict, description="Execution status for each step.")
    links: Dict[str, str] = Field(default_factory=dict, description="HATEOAS navigation links.")

class ExecutionListResponse(BaseModel):
    """
    DTO for a paginated list of execution runs.
    """
    items: list[ExecutionResponse]
    total: int
    limit: int
    skip: int
