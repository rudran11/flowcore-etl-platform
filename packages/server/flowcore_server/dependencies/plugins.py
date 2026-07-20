from fastapi import Depends
from flowcore_engine.plugins.manager import PluginManager
from flowcore_server.dependencies.engine import get_plugin_manager
from flowcore_server.services.plugin_service import PluginService
from flowcore_server.application.plugin_app import PluginApplication

def get_plugin_application(manager: PluginManager = Depends(get_plugin_manager)) -> PluginApplication:
    service = PluginService(manager)
    return PluginApplication(service)
