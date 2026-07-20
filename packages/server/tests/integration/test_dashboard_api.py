import pytest
from httpx import AsyncClient, ASGITransport
from flowcore_server.main import app
from flowcore_server.dependencies.core import get_uow
from flowcore_server.repositories.in_memory.uow import InMemoryUnitOfWork

@pytest.mark.asyncio
async def test_get_dashboard_empty_db():
    """Test dashboard aggregation on an empty database (using in-memory for simple check)."""
    in_mem_uow = InMemoryUnitOfWork()
    app.dependency_overrides[get_uow] = lambda: in_mem_uow
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/")
        
    assert response.status_code == 200
    
    data = response.json()
    assert data["statistics"]["total_pipelines"] == 0
    assert data["statistics"]["total_runs"] == 0
    assert data["statistics"]["success_rate"] == 0.0
    assert data["statistics"]["avg_duration_ms"] == 0.0
    
    assert data["execution_summary"]["completed"] == 0
    assert data["execution_summary"]["failed"] == 0
    
    assert len(data["trends"]) == 7
    for trend in data["trends"]:
        assert trend["completed"] == 0
        assert trend["failed"] == 0
        
    assert len(data["recent_runs"]) == 0
    assert data["health"]["server"] == "healthy"
    
    app.dependency_overrides.clear()

