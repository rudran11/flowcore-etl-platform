import pytest
from pydantic import ValidationError
from flowcore.models.pipeline.template import Template

def test_template_creation():
    template = Template(
        id="tmpl-001",
        name="Standard Postgres Extract",
        template_type="STEP",
        default_parameters={"table_name": "users"},
        body={"connector_id": "postgres", "query": "SELECT * FROM {{table_name}}"}
    )
    assert template.id == "tmpl-001"
    assert template.template_type == "STEP"
    assert template.default_parameters["table_name"] == "users"
    assert "query" in template.body
