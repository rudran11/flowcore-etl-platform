import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep

def test_execution_step_creation():
    step = ExecutionStep(
        step_id="extract_postgres",
        connector_id="prod-db",
        depends_on=["wait_for_file"],
        parameters={"query": "SELECT * FROM sales"}
    )
    assert step.step_id == "extract_postgres"
    assert step.connector_id == "prod-db"
    assert "wait_for_file" in step.depends_on
    assert step.parameters["query"] == "SELECT * FROM sales"

def test_execution_step_no_depends_on():
    step = ExecutionStep(
        step_id="extract_postgres",
        connector_id="prod-db"
    )
    assert step.depends_on == []
    assert step.parameters == {}
