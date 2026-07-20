import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app
from flowcore_server.dependencies.core import get_pipeline_repository
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_dummy_pipeline():
    repo = get_pipeline_repository()
    pipeline = PipelineVersion(
        id="int-pv-1",
        pipeline_id="int-pipe-1",
        version="1.0.0",
        steps=[]
    )
    graph = DependencyGraph(nodes={}, edges=[])
    repo.seed(pipeline, graph)

def test_execute_pipeline_integration():
    res = client.post("/api/v1/pipelines/int-pipe-1/versions/1.0.0/execute", json={"parameters": {}})
    assert res.status_code == 202
    data = res.json()
    assert data["pipeline_id"] == "int-pipe-1"
    assert data["pipeline_version"] == "1.0.0"
    assert data["status"] == "PENDING"
    assert "run_id" in data
    assert "self" in data["links"]
    assert "cancel" in data["links"]

def test_execute_missing_pipeline_integration():
    res = client.post("/api/v1/pipelines/missing/versions/1.0.0/execute", json={"parameters": {}})
    assert res.status_code in (404, 400)
    assert res.json()["flowcore_code"] == "FLOWCORE-3001"
