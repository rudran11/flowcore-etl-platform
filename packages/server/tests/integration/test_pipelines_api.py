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

def test_execute_pipeline_integration():
    res = client.post("/api/v1/pipelines/int-pipe-1/versions/1.0.0/execute", json={"parameters": {}})
    assert res.status_code == 202
    data = res.json()
    assert data["pipeline_id"] == "int-pipe-1"
    assert isinstance(data["pipeline_version"], str)
    assert data["status"] == "PENDING"
    assert "run_id" in data
    assert "self" in data["links"]
    assert "cancel" in data["links"]

def test_execute_missing_pipeline_integration():
    res = client.post("/api/v1/pipelines/missing/versions/1.0.0/execute", json={"parameters": {}})
    assert res.status_code in (404, 400)
    assert res.json()["flowcore_code"] == "FLOWCORE-3001"
