# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Plugin metadata schema."""

from enum import Enum
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class PluginType(str, Enum):
    """Defines the operational category of a plugin."""
    SOURCE = "SOURCE"
    DESTINATION = "DESTINATION"
    TRANSFORMER = "TRANSFORMER"
    HOOK = "HOOK"

class Plugin(MetadataEntity):
    """
    Represents an executable extension registered within the FlowCore platform.
    """
    name: str = Field(..., description="The human-readable name of the plugin.")
    plugin_type: PluginType = Field(..., description="The category of the plugin.")
    version: str = Field(..., description="Semantic version of the plugin.")
    entrypoint: str = Field(..., description="The python module path or docker image to execute.")
