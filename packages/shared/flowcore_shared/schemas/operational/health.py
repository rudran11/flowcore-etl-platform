# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Health record schema."""

from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class HealthRecord(MetadataEntity):
    """
    Represents the operational health status of a platform component.
    """
    component_id: str = Field(..., description="The identifier of the component (e.g., engine-worker-1).")
    status: str = Field(..., description="The current status (e.g., HEALTHY, DEGRADED, DOWN).")
    message: str = Field(..., description="A detailed health message or error traceback.")
