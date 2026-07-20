# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Audit log schema."""

from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class AuditLog(MetadataEntity):
    """
    Immutable record of a platform action performed by an actor.
    """
    actor_id: str = Field(..., description="The user, service account, or system that performed the action.")
    action_type: str = Field(..., description="The type of action performed (e.g., CREATE_PIPELINE, UPDATE_CONNECTOR).")
    resource_id: str = Field(..., description="The ID of the affected resource.")
    resource_type: str = Field(..., description="The type of the affected resource.")
