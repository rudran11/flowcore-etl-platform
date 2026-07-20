from fastapi import APIRouter, Depends
from typing import List
from flowcore_engine.plugins.manager import PluginManager
from flowcore_server.dependencies.engine import get_plugin_manager
from flowcore_server.services.plugin_service import PluginService
from flowcore_server.application.plugin_app import PluginApplication
from flowcore_server.models.plugin import PluginResponse

router = APIRouter(prefix="/plugins", tags=["Plugins"])

def get_plugin_application(manager: PluginManager = Depends(get_plugin_manager)) -> PluginApplication:
    service = PluginService(manager)
    return PluginApplication(service)

@router.get("", response_model=List[PluginResponse], summary="List Plugins")
async def list_plugins(app: PluginApplication = Depends(get_plugin_application)):
    """
    Retrieves all registered plugins available in the engine.
    """
    return app.list_plugins()

@router.get("/{plugin_id}", response_model=PluginResponse, summary="Get Plugin")
async def get_plugin(plugin_id: str, app: PluginApplication = Depends(get_plugin_application)):
    """
    Retrieves detailed metadata for a specific plugin.
    """
    return app.get_plugin(plugin_id)
