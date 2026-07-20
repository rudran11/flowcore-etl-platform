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
        id="int-pv-2",
        pipeline_id="int-pipe-2",
        version="1.0.0",
        steps=[]
    )
    graph = DependencyGraph(nodes={}, edges=[])
    repo.seed(pipeline, graph)

def test_run_lifecycle_integration():
    # 1. Execute
    res = client.post("/api/v1/pipelines/int-pipe-2/versions/1.0.0/execute", json={"parameters": {}})
    assert res.status_code == 202
    run_id = res.json()["run_id"]
    
    # 2. Get status
    res_get = client.get(f"/api/v1/runs/{run_id}")
    assert res_get.status_code == 200
    assert res_get.json()["run_id"] == run_id

    # 3. Cancel
    res_cancel = client.post(f"/api/v1/runs/{run_id}/cancel")
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"

    # 4. Idempotent cancel
    res_cancel2 = client.post(f"/api/v1/runs/{run_id}/cancel")
    assert res_cancel2.status_code == 200
    assert res_cancel2.json()["status"] == "CANCELLED"
    
def test_unknown_run_integration():
    res = client.get("/api/v1/runs/missing-run-id")
    assert res.status_code in (404, 400)
    assert res.json()["flowcore_code"] == "FLOWCORE-3001"
