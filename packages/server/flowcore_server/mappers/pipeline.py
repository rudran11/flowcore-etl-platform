from flowcore.models.pipeline.pipeline import Pipeline
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore_server.models.pipeline import PipelineResponse, StepResponse

def map_pipeline_to_response(pipeline: Pipeline, version: PipelineVersion) -> PipelineResponse:
    """
    Maps internal Shared Pipeline and PipelineVersion models to a public API PipelineResponse DTO.
    """
    steps = []
    dependencies = {}
    
    for step in version.steps:
        steps.append(StepResponse(id=step.step_id, plugin_id=step.connector_id, name=None))
        if step.depends_on:
            dependencies[step.step_id] = step.depends_on
            
    return PipelineResponse(
        id=pipeline.id,
        name=pipeline.name,
        version=version.version,
        description=pipeline.description,
        steps=steps,
        dependencies=dependencies
    )
