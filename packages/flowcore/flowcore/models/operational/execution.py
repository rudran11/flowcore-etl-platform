# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Execution run schema."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity
from flowcore_shared.schemas.base.enums import ExecutionState
from pydantic import Field, BaseModel

class ExecutionAttempt(BaseModel):
    """
    Represents a specific attempt of a pipeline execution step.
    """
    attempt_number: int = Field(..., description="The retry attempt number (0 for initial).")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the attempt started.")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the attempt ended.")
    error_message: Optional[str] = Field(None, description="Error message if the attempt failed.")
    error_category: Optional[str] = Field(None, description="Category of the error (e.g. NetworkTimeoutError).")
    status: ExecutionState = Field(..., description="The final state of this attempt.")

class ExecutionStepRun(MetadataEntity):
    """
    Represents the execution state of a single step within a pipeline run.
    """
    step_id: str = Field(..., description="The ID of the step.")
    status: ExecutionState = Field(default=ExecutionState.PENDING, description="The current state of this step.")
    start_time: Optional[datetime] = Field(None, description="Timestamp when the step transitioned to RUNNING.")
    end_time: Optional[datetime] = Field(None, description="Timestamp when the step reached a terminal state.")
    duration_ms: Optional[float] = Field(None, description="Total duration of the step execution in milliseconds.")
    retry_count: int = Field(default=0, description="Number of times this step has been retried.")
    error_message: Optional[str] = Field(None, description="Error message if the step failed.")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs produced by this step.")
    logs: List[str] = Field(default_factory=list, description="Execution logs for this step.")
    attempt_history: List[ExecutionAttempt] = Field(default_factory=list, description="History of execution attempts for this step.")

class ExecutionRun(MetadataEntity):
    """
    Represents a specific runtime execution of a PipelineVersion.
    """
    workspace_id: str = Field(..., description="The workspace this execution belongs to.")
    pipeline_id: str = Field(..., description="The parent pipeline ID.")
    pipeline_version_id: str = Field(..., description="The specific pipeline version ID executed.")
    status: ExecutionState = Field(default=ExecutionState.PENDING, description="The current state of the execution.")
    trigger_type: str = Field(..., description="The event that caused this run (e.g., MANUAL, SCHEDULED).")
    trigger_context: Dict[str, Any] = Field(default_factory=dict, description="Context about the trigger (e.g., webhook payload, API key ID).")
    start_time: Optional[datetime] = Field(None, description="Timestamp when the run transitioned to RUNNING.")
    end_time: Optional[datetime] = Field(None, description="Timestamp when the run reached a terminal state.")
    attempt_number: int = Field(default=0, description="The execution attempt number. Incremented by 1 on retry.")
    worker_id: Optional[str] = Field(None, description="The ID of the worker that claimed this run.")
    claimed_at: Optional[datetime] = Field(None, description="Timestamp when the run was claimed by a worker.")
    lease_expires_at: Optional[datetime] = Field(None, description="Timestamp when the worker's execution lease expires. Used for crash recovery.")
    steps: Dict[str, ExecutionStepRun] = Field(default_factory=dict, description="Map of step_id to its execution state.")
    error_message: Optional[str] = Field(None, description="Global error message if the pipeline failed before/outside steps.")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Global outputs collected from the execution steps.")
