import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from flowcore.engine.exceptions.plugin import PluginLoadError
from flowcore_server.main import app
from pydantic import BaseModel

router = APIRouter()

class MockModel(BaseModel):
    field: int

@router.get("/trigger-plugin-error")
async def trigger_plugin():
    raise PluginLoadError("dummy-plugin", "Failed to load")

@router.post("/trigger-validation-error")
async def trigger_validation(model: MockModel):
    return model

@router.get("/trigger-value-error")
async def trigger_value():
    raise ValueError("Invalid value")

@router.get("/trigger-unhandled-error")
async def trigger_unhandled():
    raise Exception("Unhandled")

app.include_router(router)

def test_plugin_load_error_handler(client):
    response = client.get("/trigger-plugin-error")
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == 500
    assert data["flowcore_code"] == "FLOWCORE-1001"

def test_validation_error_handler(client):
    response = client.post("/trigger-validation-error", json={"field": "not-an-int"})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == 422
    assert data["flowcore_code"] == "FLOWCORE-2001"

def test_value_error_handler(client):
    response = client.get("/trigger-value-error")
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert data["flowcore_code"] == "FLOWCORE-3001"

def test_global_exception_handler(client):
    response = client.get("/trigger-unhandled-error")
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == 500
    assert data["flowcore_code"] == "FLOWCORE-9999"
