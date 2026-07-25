# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
import sys
import importlib.util
import inspect
from typing import Dict, List, Type
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_engine.exceptions.plugin import PluginLoadError
from .enums import PluginLifecycleState

class PluginManager:
    """
    Discovers, loads, and validates FlowCore plugins.
    Strictly isolated from plugin execution and state management.
    """

    def __init__(self) -> None:
        # Registries mapping plugin_id -> internal tracking data
        self._metadata_registry: Dict[str, PluginMetadata] = {}
        self._instance_registry: Dict[str, BasePlugin] = {}
        self._lifecycle_registry: Dict[str, PluginLifecycleState] = {}

    def discover_plugins(self, directories: List[str]) -> None:
        """
        Scans given directories, dynamically loads python files, validates BasePlugins,
        and instantiates them into the internal registry.
        """
        discovered_classes: List[Type[BasePlugin]] = []

        for directory in directories:
            if not os.path.exists(directory):
                continue
            
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        plugin_classes = self._load_from_path(file_path)
                        discovered_classes.extend(plugin_classes)

        # Validate and Instantiate
        for cls in discovered_classes:
            self._validate_and_register(cls)

    def _load_from_path(self, file_path: str) -> List[Type[BasePlugin]]:
        """Dynamically imports a module and finds BasePlugin subclasses."""
        module_name = os.path.basename(file_path)[:-3]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"Could not load spec for {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise PluginLoadError(f"Malformed plugin import in {file_path}: {str(e)}") from e

        plugin_classes = []
        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                plugin_classes.append(obj)
                
        return plugin_classes

    def _validate_and_register(self, plugin_cls: Type[BasePlugin]) -> None:
        """Validates a plugin class and its metadata, then instantiates it."""
        try:
            # Instantiate to access properties.
            # We enforce that plugins must be instantiable without arguments.
            instance = plugin_cls()
        except Exception as e:
            raise PluginLoadError(f"Failed to instantiate {plugin_cls.__name__}: {str(e)}") from e
            
        try:
            metadata = instance.metadata
        except Exception as e:
            raise PluginLoadError(f"Plugin {plugin_cls.__name__} failed to provide metadata: {str(e)}") from e
            
        if not isinstance(metadata, PluginMetadata):
            raise PluginLoadError(f"Plugin {plugin_cls.__name__} metadata must be a PluginMetadata instance.")
            
        plugin_id = metadata.plugin_id
        
        # Verify uniqueness
        if plugin_id in self._metadata_registry:
            raise PluginLoadError(f"Duplicate plugin_id detected: {plugin_id}")
            
        # Verify execute callable
        if not hasattr(instance, "execute"):
            raise PluginLoadError(f"Plugin {plugin_id} is missing 'execute' method.")
        if not callable(getattr(instance, "execute")):
            raise PluginLoadError(f"Plugin {plugin_id} 'execute' attribute is not callable.")
            
        # At this point, Pydantic has already validated version semantics and plugin_type.
        
        # Dependency check
        for dep in metadata.dependencies:
            if dep not in self._metadata_registry:
                self._lifecycle_registry[plugin_id] = PluginLifecycleState.ERROR
                raise PluginLoadError(f"Plugin {plugin_id} missing dependency: {dep}")
        
        # Compatibility check (mock simple check for now, e.g., if starts with < we can fail, but let's just log or accept >=1.0.0)
        if not metadata.compatibility.startswith(">="):
            # Just a stub for more complex semver check
            pass

        # Register cleanly
        self._lifecycle_registry[plugin_id] = PluginLifecycleState.VALIDATED
        self._metadata_registry[plugin_id] = metadata
        self._instance_registry[plugin_id] = instance
        self._lifecycle_registry[plugin_id] = PluginLifecycleState.READY

    def get_plugin(self, plugin_id: str) -> BasePlugin:
        """Retrieves a fully validated plugin instance."""
        if plugin_id not in self._instance_registry:
            raise PluginLoadError(f"Plugin {plugin_id} not found in registry.")
        return self._instance_registry[plugin_id]

    def list_plugins(self) -> List[PluginMetadata]:
        """Retrieves a list of all registered plugin metadata."""
        return list(self._metadata_registry.values())

    def get_metadata(self, plugin_id: str) -> PluginMetadata:
        """Retrieves plugin metadata independently of the plugin instance."""
        if plugin_id not in self._metadata_registry:
            raise PluginLoadError(f"Plugin metadata for {plugin_id} not found in registry.")
        return self._metadata_registry[plugin_id]
        
    def get_lifecycle_state(self, plugin_id: str) -> PluginLifecycleState:
        """Retrieves the current diagnostic lifecycle state of the plugin."""
        if plugin_id not in self._lifecycle_registry:
            raise PluginLoadError(f"Plugin {plugin_id} not found in registry.")
        return self._lifecycle_registry[plugin_id]
