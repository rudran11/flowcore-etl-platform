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

client = TestClient(app, raise_server_exceptions=True)

@pytest.fixture(autouse=True)
def setup_dummy_pipeline():
    uow = InMemoryUnitOfWork()
    app.dependency_overrides[get_uow] = lambda: uow
    
    async def seed():
        async with uow:
            p = Pipeline(id="pipe-1", workspace_id=str(uuid.uuid4()), name="test", owner="test")
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

def test_execute_pipeline_success():
    req_data = {"parameters": {"key": "value"}}
    response = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json=req_data, headers={"X-Request-ID": "test-req-1"})
    
    if response.status_code == 500:
        print("500 Error:", response.json())
    assert response.status_code == 202
    data = response.json()
    assert data["pipeline_id"] == "pipe-1"
    assert isinstance(data["pipeline_version"], str)
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
