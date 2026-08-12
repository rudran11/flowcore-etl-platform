from fastapi.testclient import TestClient
from flowcore_server.main import create_app
from flowcore_server.dependencies.auth import get_current_user, require_permissions
from flowcore_shared.schemas.auth import UserInDB

app = create_app()

def override_require_permissions(perms):
    def _override(x_workspace_id: str = "1b589417-3d12-42de-8e50-9d3329747d21"):
        return UserInDB(id="00000000-0000-0000-0000-000000000000", email="test@test.com", username="test", is_active=True, is_superuser=False, created_at="2023-01-01", updated_at="2023-01-01")
    return _override

# Patch the specific dependency
app.dependency_overrides[require_permissions] = override_require_permissions

client = TestClient(app)

response = client.get("/api/v1/pipelines?limit=5", headers={"X-Workspace-ID": "1b589417-3d12-42de-8e50-9d3329747d21"})
print("STATUS:", response.status_code)
print("BODY:", response.json())
