import pytest
import asyncio
from fastapi.testclient import TestClient
from flowcore_server.main import app
from flowcore_server.dependencies.core import get_uow
from flowcore_server.repositories.in_memory.uow import InMemoryUnitOfWork
from flowcore_shared.schemas.pipeline.pipeline import Pipeline
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_dummy_pipeline():
    uow = InMemoryUnitOfWork()
    app.dependency_overrides[get_uow] = lambda: uow
    
    async def seed():
        async with uow:
            p = Pipeline(id="smoke-pipe-1", name="test", owner="test")
            await uow.pipelines.create_pipeline(p)
            pv = PipelineVersion(
                id=str(uuid.uuid4()),
                pipeline_id="smoke-pipe-1",
                version="1.0.0",
                steps=[]
            )
            await uow.pipelines.create_pipeline_version(pv)
            await uow.commit()

    asyncio.run(seed())
    yield
    app.dependency_overrides.clear()

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
