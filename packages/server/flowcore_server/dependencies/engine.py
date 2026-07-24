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
                import os
                
                # In Milestone 4, we initialized a blank/default manager.
                # Now we discover mock plugins to showcase the Plugin Hub.
                _plugin_manager_instance = PluginManager()
                
                # Resolve path to packages/server/mock_plugins
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                mock_plugins_dir = os.path.join(base_dir, "mock_plugins")
                
                _plugin_manager_instance.discover_plugins([mock_plugins_dir])
    
    return _plugin_manager_instance
