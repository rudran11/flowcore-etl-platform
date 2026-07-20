from typing import Optional
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
