from pydantic import BaseModel, Field

class PipelineVersionCreate(BaseModel):
    version_tag: str = Field(..., description="A unique tag or hash for this version (e.g. 'v1.1', 'draft')")
    dsl_definition: dict = Field(..., description="The full YAML or JSON representation of the pipeline.")
    graph_definition: dict = Field(..., description="The UI graph representation (nodes/edges).")

from flowcore.models.pipeline import PipelineVersion

class PipelineVersionResponse(PipelineVersion):
    pass
