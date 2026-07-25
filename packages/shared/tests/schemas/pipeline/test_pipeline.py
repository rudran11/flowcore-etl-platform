import pytest
from pydantic import ValidationError
from flowcore.models.pipeline.pipeline import Pipeline

def test_pipeline_creation():
    pipeline = Pipeline(
        id="etl-001",
        workspace_id="00000000-0000-0000-0000-000000000000",
        name="Daily Sales Extract",
        owner="Data Platform Team",
        tags=["sales", "daily", "critical"]
    )
    assert pipeline.id == "etl-001"
    assert pipeline.owner == "Data Platform Team"
    assert "critical" in pipeline.tags

def test_pipeline_missing_owner():
    with pytest.raises(ValidationError):
        Pipeline(workspace_id="00000000-0000-0000-0000-000000000000", id="etl-001",
            name="Daily Sales Extract"
        )
