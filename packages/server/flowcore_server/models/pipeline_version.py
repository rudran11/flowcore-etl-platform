from pydantic import BaseModel, Field

from typing import List, Dict, Any, Optional

class PipelineStepCreate(BaseModel):
    step_id: str
    plugin_id: str
    depends_on: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Optional[Dict[str, Any]] = None

class PipelineVersionCreate(BaseModel):
    version_tag: str = Field(..., description="A unique tag or hash for this version (e.g. 'v1.1', 'draft')")
    steps: List[PipelineStepCreate] = Field(default_factory=list, description="List of pipeline steps")
    dsl_definition: dict = Field(..., description="The full YAML or JSON representation of the pipeline.")
    graph_definition: dict = Field(..., description="The UI graph representation (nodes/edges).")

from flowcore.models.pipeline import PipelineVersion

class PipelineVersionResponse(PipelineVersion):
    pass
