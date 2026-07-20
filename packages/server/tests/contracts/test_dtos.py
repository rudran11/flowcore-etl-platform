import pytest
from pydantic import ValidationError
from flowcore_server.models.execution import ExecutionResponse, ExecutionRequest
from flowcore_server.models.plugin import PluginResponse
from flowcore_server.models.pipeline import PipelineResponse, StepResponse

def test_execution_response_strict():
    # Missing run_id should fail
    with pytest.raises(ValidationError):
        ExecutionResponse(pipeline_id="pipe1", status="PENDING", pipeline_version="1.0.0", submitted_at="2026-07-20T12:00:00Z")
    
    # Valid
    resp = ExecutionResponse(
        run_id="run1", 
        pipeline_id="pipe1", 
        pipeline_version="1.0.0",
        status="PENDING", 
        submitted_at="2026-07-20T12:00:00Z"
    )
    assert resp.run_id == "run1"

def test_plugin_response_strict():
    with pytest.raises(ValidationError):
        PluginResponse()
        
    resp = PluginResponse(plugin_id="plugin1", name="My Plugin", version="1.0.0", plugin_type="CONNECTOR")
    assert resp.name == "My Plugin"
