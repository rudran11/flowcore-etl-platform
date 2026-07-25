import asyncio
from fastapi.testclient import TestClient
from flowcore_server.main import app
from flowcore_shared.schemas.auth.user import UserInDB

def dummy_user():
    from datetime import datetime
    return UserInDB(
        id="00000000-0000-0000-0000-000000000000",
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=True,
        password_hash="fake",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

for route in app.routes:
    if hasattr(route, "dependant"):
        for dep in route.dependant.dependencies:
            if getattr(dep.call, "__name__", "") == "permission_checker":
                app.dependency_overrides[dep.call] = dummy_user

client = TestClient(app, raise_server_exceptions=False)

def test_datasets():
    res = client.get("/api/v1/datasets")
    print("GET /api/v1/datasets ->", res.status_code)
    print(res.text)

if __name__ == "__main__":
    test_datasets()
