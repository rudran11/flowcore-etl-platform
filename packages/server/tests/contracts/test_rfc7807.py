import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app

client = TestClient(app)

def test_rfc7807_404():
    res = client.get("/api/v1/unknown")
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data

def test_rfc7807_422():
    res = client.post("/api/v1/pipelines/pipe/versions/1/execute", json="not a dict")
    assert res.status_code == 422
    data = res.json()
    assert data["flowcore_code"] == "FLOWCORE-2001"
    assert data["status"] == 422
    assert "type" in data
    assert "title" in data
    assert "detail" in data
    assert "instance" in data
