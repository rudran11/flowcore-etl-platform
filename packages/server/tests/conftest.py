import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app

@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
