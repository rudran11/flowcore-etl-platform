import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep

def test_pipeline_version_creation():
    step1 = ExecutionStep(step_id="step1", connector_id="conn1")
    step2 = ExecutionStep(step_id="step2", connector_id="conn2", depends_on=["step1"])
    
    version = PipelineVersion(
        id="version-hash-abc",
        pipeline_id="etl-001",
        version="1.0.0",
        steps=[step1, step2]
    )
    assert version.id == "version-hash-abc"
    assert version.pipeline_id == "etl-001"
    assert len(version.steps) == 2
    assert version.steps[1].depends_on == ["step1"]
