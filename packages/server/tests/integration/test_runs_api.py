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
def setup_integration_data():
    uow = InMemoryUnitOfWork()
    app.dependency_overrides[get_uow] = lambda: uow
    
    # Mock background strategy
    class MockBackgroundStrategy:
        def submit(self, run_id, func, *args, **kwargs):
            pass
        def shutdown(self):
            pass
            
    from flowcore_server.dependencies.core import get_background_strategy
    app.dependency_overrides[get_background_strategy] = lambda: MockBackgroundStrategy()
    
    async def seed():
        async with uow:
            p = Pipeline(id="int-pipe-1", workspace_id=str(uuid.uuid4()), name="test", owner="test")
            await uow.pipelines.create_pipeline(p)
            pv = PipelineVersion(
                id=str(uuid.uuid4()),
                pipeline_id="int-pipe-1",
                version="1.0.0",
                steps=[]
            )
            await uow.pipelines.create_pipeline_version(pv)
            await uow.commit()

    asyncio.run(seed())
    yield
    app.dependency_overrides.clear()

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
    assert res.status_code == 404
    assert res.json()["detail"] == "Run not found"
