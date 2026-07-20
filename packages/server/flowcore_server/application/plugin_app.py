from typing import List
from flowcore_server.services.plugin_service import PluginService
from flowcore_server.models.plugin import PluginResponse
from flowcore_server.mappers.plugin import map_plugin_to_response

class PluginApplication:
    """
    Orchestrates plugin discovery use-cases.
    Belongs to the Application Layer.
    """
    def __init__(self, service: PluginService):
        self._service = service

    def list_plugins(self) -> List[PluginResponse]:
        internal_plugins = self._service.get_all_plugins()
        return [map_plugin_to_response(p) for p in internal_plugins]

    def get_plugin(self, plugin_id: str) -> PluginResponse:
        internal_plugin = self._service.get_plugin(plugin_id)
        return map_plugin_to_response(internal_plugin)
