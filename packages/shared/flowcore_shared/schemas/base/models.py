# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Base Pydantic models for FlowCore."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

def utc_now() -> datetime:
    """Returns the current UTC timestamp."""
    return datetime.now(timezone.utc)

class FlowCoreBaseModel(BaseModel):
    """
    The absolute root Pydantic model for all FlowCore metadata schemas.
    Configured for strict validation and frozen by default to ensure immutability
    of runtime metadata schemas.
    """
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True
    )

class MetadataEntity(FlowCoreBaseModel):
    """
    Base model for any primary logical metadata entity requiring identity
    and temporal tracking.
    """
    id: str = Field(..., description="Universally unique identifier for the entity.")
    created_at: datetime = Field(default_factory=utc_now, description="Timestamp of entity creation.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last entity mutation.")
