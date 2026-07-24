# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Execution run schema."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity
from flowcore_shared.schemas.base.enums import ExecutionState
class ExecutionStepRun(MetadataEntity):
    """
    Represents the execution state of a single step within a pipeline run.
    """
    step_id: str = Field(..., description="The ID of the step.")
    status: ExecutionState = Field(default=ExecutionState.PENDING, description="The current state of this step.")
    start_time: Optional[datetime] = Field(None, description="Timestamp when the step transitioned to RUNNING.")
    end_time: Optional[datetime] = Field(None, description="Timestamp when the step reached a terminal state.")
    retry_count: int = Field(default=0, description="Number of times this step has been retried.")
    error_message: Optional[str] = Field(None, description="Error message if the step failed.")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs produced by this step.")
    logs: List[str] = Field(default_factory=list, description="Execution logs for this step.")

class ExecutionRun(MetadataEntity):
    """
    Represents a specific runtime execution of a PipelineVersion.
    """
    pipeline_id: str = Field(..., description="The parent pipeline ID.")
    pipeline_version_id: str = Field(..., description="The specific pipeline version ID executed.")
    status: ExecutionState = Field(default=ExecutionState.PENDING, description="The current state of the execution.")
    trigger_type: str = Field(..., description="The event that caused this run (e.g., MANUAL, SCHEDULED).")
    start_time: Optional[datetime] = Field(None, description="Timestamp when the run transitioned to RUNNING.")
    end_time: Optional[datetime] = Field(None, description="Timestamp when the run reached a terminal state.")
    steps: Dict[str, ExecutionStepRun] = Field(default_factory=dict, description="Map of step_id to its execution state.")
    error_message: Optional[str] = Field(None, description="Global error message if the pipeline failed before/outside steps.")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Global outputs collected from the execution steps.")
