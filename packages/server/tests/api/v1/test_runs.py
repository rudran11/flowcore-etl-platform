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
    
    # Mock background strategy to prevent TestClient from blocking on execution
    class MockBackgroundStrategy:
        def submit(self, run_id, func, *args, **kwargs):
            pass
        def shutdown(self):
            pass
            
    from flowcore_server.dependencies.core import get_background_strategy
    app.dependency_overrides[get_background_strategy] = lambda: MockBackgroundStrategy()

    
    async def seed():
        async with uow:
            p = Pipeline(id="pipe-1", name="test", owner="test")
            await uow.pipelines.create_pipeline(p)
            pv = PipelineVersion(
                id=str(uuid.uuid4()),
                pipeline_id="pipe-1",
                version="1.0.0",
                steps=[]
            )
            await uow.pipelines.create_pipeline_version(pv)
            await uow.commit()

    asyncio.run(seed())
    yield
    app.dependency_overrides.clear()

def test_get_run_status():
    # 1. Create run
    res = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json={"parameters": {}}, headers={"X-Request-ID": "test-req-2"})
    assert res.status_code == 202
    run_id = res.json()["run_id"]
    
    # 2. Get run
    res_get = client.get(f"/api/v1/runs/{run_id}", headers={"X-Request-ID": "test-req-2"})
    assert res_get.status_code == 200
    assert res_get.json()["run_id"] == run_id
    assert res_get.headers["X-Request-ID"] == "test-req-2"

def test_cancel_run_idempotency():
    # 1. Create run
    res = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json={"parameters": {}})
    run_id = res.json()["run_id"]
    
    # 2. Cancel run
    res_cancel1 = client.post(f"/api/v1/runs/{run_id}/cancel")
    if res_cancel1.status_code != 200:
        print(res_cancel1.json())
    assert res_cancel1.status_code == 200
    assert res_cancel1.json()["status"] == "CANCELLED"
    
    # 3. Cancel again
    res_cancel2 = client.post(f"/api/v1/runs/{run_id}/cancel")
    assert res_cancel2.status_code == 200
    assert res_cancel2.json()["status"] == "CANCELLED"

def test_get_unknown_run():
    res = client.get("/api/v1/runs/unknown-run-id")
    assert res.status_code == 404
