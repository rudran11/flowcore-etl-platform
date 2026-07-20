# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Connector metadata schema."""

from typing import Any, Dict
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class Connector(MetadataEntity):
    """
    Represents a configured instance of a Plugin (e.g., a specific database connection).
    """
    plugin_id: str = Field(..., description="The ID of the Plugin this connector instantiates.")
    name: str = Field(..., description="The human-readable name of this connector instance.")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Configuration parameters for the plugin. May contain SecretReferences."
    )
