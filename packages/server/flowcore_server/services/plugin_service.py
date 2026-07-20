from typing import List
from flowcore_engine.plugins.manager import PluginManager
from flowcore_shared.plugins.models import PluginMetadata

class PluginService:
    """
    Thin wrapper around the Engine's PluginManager.
    Belongs to the Service Layer.
    """
    def __init__(self, manager: PluginManager):
        self._manager = manager

    def get_all_plugins(self) -> List[PluginMetadata]:
        return self._manager.list_plugins()

    def get_plugin(self, plugin_id: str) -> PluginMetadata:
        # get_plugin raises PluginLoadError if not found
        instance = self._manager.get_plugin(plugin_id)
        return instance.metadata
