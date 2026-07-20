import pytest
import asyncio
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
        id="perf-pv-1",
        pipeline_id="perf-pipe-1",
        version="1.0.0",
        steps=[]
    )
    graph = DependencyGraph(nodes={}, edges=[])
    repo.seed(pipeline, graph)

@pytest.mark.parametrize("concurrent_requests", [10, 20, 50])
def test_parallel_execution_requests(concurrent_requests):
    import threading
    
    results = []
    
    def execute_request():
        res = client.post("/api/v1/pipelines/perf-pipe-1/versions/1.0.0/execute", json={"parameters": {}})
        results.append(res)
        
    threads = [threading.Thread(target=execute_request) for _ in range(concurrent_requests)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert len(results) == concurrent_requests
    run_ids = set()
    for res in results:
        assert res.status_code == 202
        run_ids.add(res.json()["run_id"])
        
    # Verify unique run IDs and no deadlocks
    assert len(run_ids) == concurrent_requests
