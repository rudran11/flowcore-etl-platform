# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from datetime import datetime, timezone
from typing import Optional
from pydantic import Field, field_validator
from uuid import uuid4
from flowcore_shared.schemas.base.models import FlowCoreBaseModel

class DomainEvent(FlowCoreBaseModel):
    """
    Base class for all domain events in FlowCore.
    Domain events represent business facts and are immutable.
    """
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the event")
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the event")
    event_type: str = Field(..., description="The fully qualified type name of the event")
    event_version: int = Field(default=1, description="Version of the event schema for future compatibility")
    request_id: Optional[str] = Field(default=None, description="HTTP Request ID that initiated the event sequence")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for distributed tracing")

    @field_validator('occurred_at')
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
