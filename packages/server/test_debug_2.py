import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app

def dummy_user():
    from flowcore_shared.schemas.auth.user import UserInDB
    return UserInDB(
        id="00000000-0000-0000-0000-000000000000",
        email="test@example.com",
        name="Test User",
        is_active=True,
        is_superuser=True,
        hashed_password="fake"
    )

for route in app.routes:
    if hasattr(route, "dependencies"):
        for dep in route.dependencies:
            if getattr(dep.dependency, "__name__", "") == "permission_checker":
                app.dependency_overrides[dep.dependency] = dummy_user

client = TestClient(app, raise_server_exceptions=True)

def test_debug():
    response = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json={"parameters": {}})
    print("STATUS:", response.status_code)
    try:
        print("BODY:", response.json())
    except:
        pass
