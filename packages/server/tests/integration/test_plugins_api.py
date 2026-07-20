import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app

client = TestClient(app)

def test_get_plugins_list():
    res = client.get("/api/v1/plugins")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_get_plugin_missing():
    res = client.get("/api/v1/plugins/missing-plugin-id")
    assert res.status_code == 500
    data = res.json()
    assert data["flowcore_code"] == "FLOWCORE-1001"
