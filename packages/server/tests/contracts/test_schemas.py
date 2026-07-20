import pytest
from datetime import datetime
from flowcore_server.models.plugin import PluginResponse
from flowcore_server.models.pipeline import PipelineResponse
from flowcore_server.models.execution import ExecutionResponse
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.schemas.pipeline.pipeline import Pipeline
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.mappers.plugin import map_plugin_to_response
from flowcore_server.mappers.pipeline import map_pipeline_to_response
from flowcore_server.mappers.execution import map_execution_to_response
from flowcore_shared.schemas.base.models import FlowCoreBaseModel

def test_models_do_not_inherit_from_shared():
    """Ensure DTOs are distinct from internal engine models to prevent data leaks."""
    assert not issubclass(PluginResponse, FlowCoreBaseModel)
    assert not issubclass(PipelineResponse, FlowCoreBaseModel)
    assert not issubclass(ExecutionResponse, FlowCoreBaseModel)

def test_plugin_mapper():
    internal_plugin = PluginMetadata(
        plugin_id="my-plugin",
        name="My Plugin",
        version="1.0.0",
        plugin_type=PluginType.CONNECTOR,
        author="Author",
        description="A plugin"
    )
    
    dto = map_plugin_to_response(internal_plugin)
    assert isinstance(dto, PluginResponse)
    assert dto.plugin_id == "my-plugin"
    assert dto.plugin_type == "CONNECTOR"

def test_pipeline_mapper():
    internal_pipeline = Pipeline(
        id="pipe-1",
        name="Test Pipeline",
        owner="test-owner",
        description="A pipeline"
    )
    
    step1 = ExecutionStep(step_id="step1", connector_id="c1", depends_on=[])
    step2 = ExecutionStep(step_id="step2", connector_id="c2", depends_on=["step1"])
    
    internal_version = PipelineVersion(
        id="ver-1",
        pipeline_id="pipe-1",
        version="1.0.0",
        steps=[step1, step2]
    )
    
    dto = map_pipeline_to_response(internal_pipeline, internal_version)
    assert isinstance(dto, PipelineResponse)
    assert dto.id == "pipe-1"
    assert dto.name == "Test Pipeline"
    assert len(dto.steps) == 2
    assert dto.dependencies == {"step2": ["step1"]}

def test_execution_mapper():
    now = datetime.now()
    internal_run = ExecutionRun(
        id="run-1",
        pipeline_id="pipe-1",
        pipeline_version_id="ver-1",
        status=ExecutionState.COMPLETED,
        trigger_type="MANUAL",
        start_time=now,
        end_time=now
    )
    
    outputs = {"step1": "success"}
    dto = map_execution_to_response(internal_run, outputs=outputs)
    assert isinstance(dto, ExecutionResponse)
    assert dto.run_id == "run-1"
    assert dto.status == "COMPLETED"
    assert dto.duration_ms == 0
    assert dto.outputs == outputs
