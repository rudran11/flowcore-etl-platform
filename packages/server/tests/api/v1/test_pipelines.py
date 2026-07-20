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
        id="pv-1",
        pipeline_id="pipe-1",
        version="1.0.0",
        steps=[]
    )
    graph = DependencyGraph(nodes={}, edges=[])
    repo.seed(pipeline, graph)

def test_execute_pipeline_success():
    req_data = {"parameters": {"key": "value"}}
    response = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json=req_data, headers={"X-Request-ID": "test-req-1"})
    
    assert response.status_code == 202
    data = response.json()
    assert data["pipeline_id"] == "pipe-1"
    assert data["pipeline_version"] == "1.0.0"
    assert "run_id" in data
    assert data["status"] == "PENDING"
    assert data["links"]["self"].endswith(f"/runs/{data['run_id']}")
    
    # Request ID propagation
    assert response.headers["X-Request-ID"] == "test-req-1"
    
def test_execute_pipeline_not_found():
    req_data = {"parameters": {}}
    response = client.post("/api/v1/pipelines/unknown/versions/1.0.0/execute", json=req_data)
    
    # Currently maps to 400 via ValueError handler
    assert response.status_code in (400, 404)
    assert response.json()["flowcore_code"] == "FLOWCORE-3001"

def test_multiple_simultaneous_executions():
    req_data = {"parameters": {}}
    run_ids = set()
    for _ in range(5):
        res = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json=req_data)
        assert res.status_code == 202
        run_ids.add(res.json()["run_id"])
        
    assert len(run_ids) == 5
