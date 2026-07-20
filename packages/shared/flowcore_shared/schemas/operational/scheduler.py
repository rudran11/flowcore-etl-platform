# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Scheduler trigger schema."""

from datetime import datetime
from typing import Optional
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class SchedulerTrigger(MetadataEntity):
    """
    Defines a recurring schedule for executing a pipeline.
    """
    pipeline_id: str = Field(..., description="The ID of the pipeline to trigger.")
    cron_expression: str = Field(..., description="A valid cron expression string.")
    enabled: bool = Field(True, description="Whether this trigger is currently active.")
    last_run: Optional[datetime] = Field(None, description="The timestamp of the last successful trigger.")
    next_run: Optional[datetime] = Field(None, description="The timestamp of the next scheduled trigger.")
