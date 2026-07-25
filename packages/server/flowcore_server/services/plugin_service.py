from typing import List
from flowcore.engine.plugins.manager import PluginManager
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

    def get_plugin_health(self, plugin_id: str) -> str:
        state = self._manager.get_lifecycle_state(plugin_id)
        return state.value

    def get_plugin_categories(self) -> List[str]:
        plugins = self._manager.list_plugins()
        return sorted(list(set(p.category for p in plugins)))

    def get_plugin_stats(self) -> dict:
        plugins = self._manager.list_plugins()
        total = len(plugins)
        healthy = 0
        unhealthy = 0
        disabled = 0
        
        for p in plugins:
            state = self._manager.get_lifecycle_state(p.plugin_id).value
            if state in ("READY", "VALIDATED"):
                healthy += 1
            elif state == "ERROR":
                unhealthy += 1
            else:
                disabled += 1
                
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "disabled": disabled
        }
