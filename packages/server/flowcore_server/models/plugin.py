from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class PluginResponse(BaseModel):
    """
    DTO for returning plugin metadata to the client.
    """
    plugin_id: str = Field(..., description="Unique identifier for the plugin.")
    name: str = Field(..., description="Human readable name of the plugin.")
    version: str = Field(..., description="Semantic version of the plugin.")
    plugin_type: str = Field(..., description="Type of the plugin (e.g. CONNECTOR, TRANSFORMER).")
    author: Optional[str] = Field(None, description="Author of the plugin.")
    description: Optional[str] = Field(None, description="Detailed description of the plugin.")
    category: str = Field("General", description="Category of the plugin.")
    connector_type: Optional[str] = Field(None, description="Connector type if applicable: Source | Destination | Transform.")
    capabilities: Dict[str, bool] = Field(default_factory=dict, description="Dictionary of supported capabilities.")
    supported_operations: List[str] = Field(default_factory=list, description="List of supported operations.")
    example_yaml: Optional[str] = Field(None, description="Example YAML configuration.")
    documentation: Optional[str] = Field(None, description="Detailed Markdown documentation.")
    config_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="JSON Schema for the plugin configuration.")
    flowcore_version_constraint: str = Field(">=0.9.0", description="FlowCore version compatibility.")
    dependencies: List[str] = Field(default_factory=list, description="List of plugin dependencies.")

class PluginValidationRequest(BaseModel):
    plugin_id: str
    config: Dict[str, Any]

class PluginValidationResponse(BaseModel):
    success: bool
    warnings: List[str] = []
    errors: List[str] = []
    latency_ms: Optional[int] = None

class PluginHealthResponse(BaseModel):
    status: str
    diagnostics: List[str] = []

class PluginStatsResponse(BaseModel):
    total: int
    healthy: int
    unhealthy: int
    disabled: int
