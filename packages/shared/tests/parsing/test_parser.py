import pytest
from flowcore.parsing.parser import DSLParser
from flowcore_shared.exceptions.parsing import DSLParseError

def test_parse_valid_dsl():
    data = {
        "version": "1.0",
        "pipeline": {
            "name": "ETL Extract",
            "owner": "Data Team",
            "tags": ["daily"]
        },
        "steps": [
            {
                "step_id": "extract_pg",
                "connector_id": "postgres_v1",
                "depends_on": [],
                "parameters": {"query": "SELECT 1"}
            }
        ]
    }
    
    pipeline, steps = DSLParser.parse_pipeline_dsl(data)
    
    assert pipeline.name == "ETL Extract"
    assert pipeline.owner == "Data Team"
    assert pipeline.id is not None  # Auto-generated
    
    assert len(steps) == 1
    assert steps[0].step_id == "extract_pg"
    assert steps[0].connector_id == "postgres_v1"
    assert steps[0].parameters["query"] == "SELECT 1"

def test_parse_invalid_version():
    data = {"version": "2.0"}
    with pytest.raises(DSLParseError, match="Unsupported DSL version"):
        DSLParser.parse_pipeline_dsl(data)

def test_parse_missing_pipeline():
    data = {"version": "1.0"}
    with pytest.raises(DSLParseError, match="Missing required top-level key: 'pipeline'"):
        DSLParser.parse_pipeline_dsl(data)

def test_parse_invalid_pipeline_schema():
    data = {
        "version": "1.0",
        "pipeline": {
            "name": "ETL"
            # Missing 'owner'
        }
    }
    with pytest.raises(DSLParseError, match="Pipeline validation failed: 'owner': Field required"):
        DSLParser.parse_pipeline_dsl(data)

def test_parse_invalid_step_schema():
    data = {
        "version": "1.0",
        "pipeline": {
            "name": "ETL",
            "owner": "Team"
        },
        "steps": [
            {
                "step_id": "extract"
                # Missing 'connector_id'
            }
        ]
    }
    with pytest.raises(DSLParseError, match="Step 'extract' validation failed: 'connector_id': Field required"):
        DSLParser.parse_pipeline_dsl(data)

def test_parse_invalid_root_type():
    with pytest.raises(DSLParseError, match="DSL root must be a dictionary"):
        DSLParser.parse_pipeline_dsl(["not", "a", "dict"])
