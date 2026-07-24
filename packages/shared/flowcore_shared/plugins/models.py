# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import re
from typing import List, Optional
from pydantic import Field, field_validator
from flowcore_shared.schemas.base.models import FlowCoreBaseModel
from .enums import PluginType

class PluginMetadata(FlowCoreBaseModel):
    """Immutable metadata describing a FlowCore plugin."""
    plugin_id: str = Field(..., description="Unique identifier for the plugin.")
    name: str = Field(..., description="Human readable name of the plugin.")
    version: str = Field(..., description="Semantic version of the plugin.")
    plugin_type: PluginType = Field(..., description="Type of the plugin.")
    author: str = Field(..., description="Author of the plugin.")
    description: str = Field(..., description="Brief description of the plugin's capabilities.")
    category: str = Field("General", description="Category of the plugin (e.g. Integration, Compute).")
    capabilities: List[str] = Field(default_factory=list, description="List of supported capabilities.")
    supported_operations: List[str] = Field(default_factory=list, description="List of supported operations.")
    example_yaml: Optional[str] = Field(None, description="Example YAML configuration.")
    documentation: Optional[str] = Field(None, description="Detailed Markdown documentation.")
    compatibility: str = Field(">=1.0.0", description="FlowCore version compatibility.")
    dependencies: List[str] = Field(default_factory=list, description="List of plugin dependencies.")

    @field_validator("version")
    def validate_semantic_version(cls, v: str) -> str:
        """Validates that the version string follows semantic versioning (MAJOR.MINOR.PATCH)."""
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(f"Version '{v}' is not a valid semantic version (must be X.Y.Z)")
        return v
