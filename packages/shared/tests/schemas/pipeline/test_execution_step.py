import pytest
from pydantic import ValidationError
from flowcore.models.pipeline.execution_step import ExecutionStep
from flowcore.models.pipeline.retry import RetryPolicy

def test_execution_step_creation():
    step = ExecutionStep(
        step_id="extract_db",
        connector_id="postgres_reader"
    )
    assert step.step_id == "extract_db"
    assert step.connector_id == "postgres_reader"
    assert step.depends_on == []
    assert step.parameters == {}
    assert step.retry_policy is None

def test_execution_step_with_retry_policy():
    step = ExecutionStep(
        step_id="load_api",
        connector_id="rest_api",
        retry_policy=RetryPolicy(max_attempts=10)
    )
    assert step.retry_policy is not None
    assert step.retry_policy.max_attempts == 10

def test_execution_step_no_depends_on():
    step = ExecutionStep(
        step_id="extract_postgres",
        connector_id="prod-db"
    )
    assert step.depends_on == []
    assert step.parameters == {}
