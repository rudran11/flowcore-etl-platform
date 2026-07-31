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

from flowcore.models.pipeline import Pipeline, PipelineVersion
from flowcore.models.operational.execution import ExecutionRun

class PipelinePaginatedResponse(BaseModel):
    items: List[Pipeline] = Field(..., description="List of pipelines in the current page.")
    total: int = Field(..., description="Total number of pipelines matching the filter.")
    skip: int = Field(..., description="Number of items skipped.")
    limit: int = Field(..., description="Maximum number of items returned.")

class PipelineDetailResponse(BaseModel):
    pipeline: Pipeline = Field(..., description="The core pipeline metadata.")
    versions: List[PipelineVersion] = Field(default_factory=list, description="All versions associated with the pipeline.")
    recent_runs: List[ExecutionRun] = Field(default_factory=list, description="Recent execution runs for this pipeline.")
