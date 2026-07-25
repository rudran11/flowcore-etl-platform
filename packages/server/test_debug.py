import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app

client = TestClient(app)

def test_debug():
    response = client.post("/api/v1/pipelines/pipe-1/versions/1.0.0/execute", json={"parameters": {}})
    print("422 RESPONSE:", response.json())
