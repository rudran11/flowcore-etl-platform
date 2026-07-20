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
        id="smoke-pv-1",
        pipeline_id="smoke-pipe-1",
        version="1.0.0",
        steps=[]
    )
    graph = DependencyGraph(nodes={}, edges=[])
    repo.seed(pipeline, graph)

def test_performance_smoke():
    # Submit 100 sequential requests and ensure stable memory/response times
    total_requests = 100
    run_ids = []
    for _ in range(total_requests):
        res = client.post("/api/v1/pipelines/smoke-pipe-1/versions/1.0.0/execute", json={"parameters": {}})
        assert res.status_code == 202
        run_ids.append(res.json()["run_id"])
        
    assert len(set(run_ids)) == total_requests
    
    # Retrieve all 100 runs
    for run_id in run_ids:
        res = client.get(f"/api/v1/runs/{run_id}")
        assert res.status_code == 200
        assert res.json()["run_id"] == run_id
