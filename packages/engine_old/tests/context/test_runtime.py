import pytest
import logging
from datetime import datetime, timezone
from pydantic import ValidationError
from flowcore_engine.context.runtime import RuntimeContext

def test_runtime_context_initialization():
    logger = logging.getLogger("test")
    ctx = RuntimeContext(
        run_id="run-1",
        pipeline_id="pipe-1",
        step_id="step-1",
        execution_start_time=datetime.now(timezone.utc),
        environment="development",
        working_directory="/tmp/work",
        temporary_directory="/tmp/scratch",
        parameters={"key": "value"},
        logger=logger
    )
    
    assert ctx.run_id == "run-1"
    assert ctx.parameters["key"] == "value"
    assert ctx.logger == logger

def test_runtime_context_immutability():
    logger = logging.getLogger("test")
    ctx = RuntimeContext(
        run_id="run-1",
        pipeline_id="pipe-1",
        step_id="step-1",
        execution_start_time=datetime.now(timezone.utc),
        environment="development",
        working_directory="/tmp/work",
        temporary_directory="/tmp/scratch",
        parameters={"key": "value"},
        logger=logger
    )
    
    with pytest.raises(ValidationError):
        ctx.environment = "production"
