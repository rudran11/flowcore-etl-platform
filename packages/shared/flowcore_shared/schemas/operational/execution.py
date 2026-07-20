# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Execution run schema."""

from datetime import datetime
from typing import Optional
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity
from flowcore_shared.schemas.base.enums import ExecutionState

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
