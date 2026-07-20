import pytest
from fastapi.testclient import TestClient
from flowcore_server.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
