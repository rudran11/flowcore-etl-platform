import pytest
import json
from pathlib import Path
from pydantic import ValidationError

from flowcore.parsing.loaders import load_yaml
from flowcore.parsing.parser import DSLParser
from flowcore.models.pipeline.pipeline import Pipeline
from flowcore.models.pipeline.execution_step import ExecutionStep
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.dependencies.node import Node
from flowcore.models.dependencies.edge import Edge
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_shared.exceptions.configuration import ConfigurationError
from flowcore_shared.exceptions.parsing import DSLParseError

def build_graph_from_steps(steps: list[ExecutionStep]) -> DependencyGraph:
    """Helper to convert parsed steps into a DependencyGraph for integration testing."""
    nodes = {step.step_id: Node(node_id=step.step_id) for step in steps}
    edges = []
    for step in steps:
        for dep in step.depends_on:
            edges.append(Edge(source=dep, target=step.step_id))
    return DependencyGraph(nodes=nodes, edges=edges)

def test_integration_end_to_end_happy_path(tmp_path):
    """
    1. End-to-End Happy Path
    YAML -> load_yaml -> DSLParser.parse -> Pipeline/ExecutionSteps -> DependencyGraph
    """
    yaml_content = """
    version: "1.0"
    pipeline:
      name: "Sample Pipeline"
      owner: "Integration Team"
    steps:
      - step_id: "extract"
        connector_id: "csv_connector"
      - step_id: "transform"
        connector_id: "filter_plugin"
        depends_on:
          - "extract"
      - step_id: "load"
        connector_id: "parquet_connector"
        depends_on:
          - "transform"
    """
    f = tmp_path / "pipeline.yaml"
    f.write_text(yaml_content)

    # 1. Load YAML
    data = load_yaml(f)
    
    # 2. Parse DSL
    pipeline, steps = DSLParser.parse_pipeline_dsl(data)
    
    assert pipeline.name == "Sample Pipeline"
    assert len(steps) == 3
    
    # 3. Build Graph
    graph = build_graph_from_steps(steps)
    
    # 4. Assert Topo Sort
    order = graph.get_topological_sort()
    assert order == ["extract", "transform", "load"]

def test_integration_invalid_yaml(tmp_path):
    """2. Invalid YAML should throw ConfigurationError, NOT YAMLError"""
    yaml_content = "invalid:\n  - missing_quote: \"hello\nbad_indent"
    f = tmp_path / "bad.yaml"
    f.write_text(yaml_content)
    
    with pytest.raises(ConfigurationError) as exc_info:
        load_yaml(f)
    # Ensure it's not a raw yaml.YAMLError bubbling up
    assert "Invalid YAML syntax" in str(exc_info.value)

def test_integration_invalid_dsl(tmp_path):
    """3. Invalid DSL (missing pipeline) throws DSLParseError"""
    yaml_content = """
    version: "1.0"
    steps:
      - step_id: "extract"
        connector_id: "csv_connector"
    """
    f = tmp_path / "missing_pipeline.yaml"
    f.write_text(yaml_content)
    
    data = load_yaml(f)
    with pytest.raises(DSLParseError, match="Missing required top-level key: 'pipeline'"):
        DSLParser.parse_pipeline_dsl(data)

def test_integration_invalid_dependency_graph():
    """4. Invalid Dependency Graph (Cycle) throws ValidationError"""
    step1 = ExecutionStep(step_id="A", connector_id="c1", depends_on=["B"])
    step2 = ExecutionStep(step_id="B", connector_id="c2", depends_on=["A"])
    
    with pytest.raises(ValidationError, match="contains a cycle"):
        build_graph_from_steps([step1, step2])

def test_integration_invalid_metadata():
    """5. Invalid Metadata (Wrong enum)"""
    from flowcore.models.operational.execution import ExecutionRun
    
    with pytest.raises(ValidationError):
        # 'INVALID_STATE' is not a valid ExecutionState Enum
        ExecutionRun(
            pipeline_id="p1", 
            pipeline_version_id="v1", 
            trigger_type="MANUAL", 
            status="INVALID_STATE"
        )

def test_integration_serialization():
    """6. Serialization (Pipeline -> dict -> json -> Pipeline)"""
    pipeline = Pipeline(workspace_id="00000000-0000-0000-0000-000000000000", id="test-serialize-1",
        name="Serializer Test",
        owner="Test Team",
        tags=["serialization"]
    )
    
    # Model to dict
    pipeline_dict = pipeline.model_dump()
    assert pipeline_dict["name"] == "Serializer Test"
    
    # Model to json string
    pipeline_json_str = pipeline.model_dump_json()
    assert "Serializer Test" in pipeline_json_str
    
    # JSON string to Model
    pipeline_restored = Pipeline.model_validate_json(pipeline_json_str)
    
    assert pipeline_restored.id == pipeline.id
    assert pipeline_restored.owner == pipeline.owner
    assert pipeline_restored.tags == ["serialization"]
