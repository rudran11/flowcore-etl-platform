from fastapi import APIRouter, Depends
from typing import List
from flowcore_server.dependencies.plugins import get_plugin_application
from flowcore_server.application.plugin_app import PluginApplication
from flowcore_server.models.plugin import (
    PluginResponse, PluginStatsResponse, PluginHealthResponse,
    PluginValidationRequest, PluginValidationResponse
)

router = APIRouter(prefix="/plugins", tags=["Plugins"])

@router.get("", response_model=List[PluginResponse], summary="List Plugins")
async def list_plugins(app: PluginApplication = Depends(get_plugin_application)):
    return app.list_plugins()

@router.get("/categories", response_model=List[str], summary="Get Categories")
async def get_categories(app: PluginApplication = Depends(get_plugin_application)):
    return app.get_categories()

@router.get("/stats", response_model=PluginStatsResponse, summary="Get Stats")
async def get_stats(app: PluginApplication = Depends(get_plugin_application)):
    return app.get_stats()

@router.get("/{plugin_id}", response_model=PluginResponse, summary="Get Plugin")
async def get_plugin(plugin_id: str, app: PluginApplication = Depends(get_plugin_application)):
    return app.get_plugin(plugin_id)

@router.get("/{plugin_id}/health", response_model=PluginHealthResponse, summary="Get Plugin Health")
async def get_health(plugin_id: str, app: PluginApplication = Depends(get_plugin_application)):
    return app.get_health(plugin_id)

@router.post("/validate", response_model=PluginValidationResponse, summary="Validate Plugin Configuration")
async def validate_plugin(request: PluginValidationRequest, app: PluginApplication = Depends(get_plugin_application)):
    return app.validate_plugin(request.plugin_id, request.config)
