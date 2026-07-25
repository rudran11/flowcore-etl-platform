import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app
from flowcore_server.dependencies.auth import get_current_user
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

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = dummy_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture(autouse=True)
def override_rbac():
    overridden = []
    for route in app.routes:
        if hasattr(route, "dependant"):
            for dep in route.dependant.dependencies:
                if getattr(dep.call, "__name__", "") == "permission_checker":
                    app.dependency_overrides[dep.call] = dummy_user
                    overridden.append(dep.call)
    yield
    for d in overridden:
        app.dependency_overrides.pop(d, None)

@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
