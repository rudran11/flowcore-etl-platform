import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState

def test_execution_run_creation():
    run = ExecutionRun(
        id="run-1",
        pipeline_id="etl-001",
        pipeline_version_id="v1.0.0",
        trigger_type="MANUAL"
    )
    assert run.status == ExecutionState.PENDING
    assert run.trigger_type == "MANUAL"
