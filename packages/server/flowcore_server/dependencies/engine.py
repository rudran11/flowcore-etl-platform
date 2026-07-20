import threading
from typing import Iterator
from flowcore_engine.plugins.manager import PluginManager

_plugin_manager_instance = None
_plugin_manager_lock = threading.Lock()

def get_plugin_manager() -> PluginManager:
    """
    FastAPI dependency that returns a singleton PluginManager instance.
    Initializes the system plugins on first call.
    """
    global _plugin_manager_instance
    if _plugin_manager_instance is None:
        with _plugin_manager_lock:
            if _plugin_manager_instance is None:
                # In Milestone 4, we initialize a blank/default manager.
                # Production would pass specific directories here.
                _plugin_manager_instance = PluginManager()
    
    return _plugin_manager_instance
