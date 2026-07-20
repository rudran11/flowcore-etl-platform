from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StepResponse(BaseModel):
    id: str = Field(..., description="Step identifier.")
    plugin_id: str = Field(..., description="Plugin identifier to execute.")
    name: Optional[str] = Field(None, description="Optional name of the step.")

class PipelineResponse(BaseModel):
    """
    DTO for returning pipeline metadata.
    """
    id: str = Field(..., description="Unique identifier of the pipeline.")
    name: str = Field(..., description="Pipeline name.")
    version: str = Field(..., description="Pipeline version.")
    description: Optional[str] = Field(None, description="Pipeline description.")
    steps: List[StepResponse] = Field(default_factory=list, description="List of pipeline steps.")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Execution dependency graph.")
