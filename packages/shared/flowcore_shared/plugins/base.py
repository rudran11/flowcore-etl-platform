# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import ABC, abstractmethod
from typing import Any
from .models import PluginMetadata

class BasePlugin(ABC):
    """
    Abstract Base Class for all FlowCore plugins.
    Plugins must remain entirely decoupled from execution engine specifics.
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Returns the immutable metadata for this plugin."""
        pass

    @abstractmethod
    def execute(self, context: Any) -> Any:
        """
        Executes the plugin logic.
        The context parameter is typed as Any to avoid coupling with the engine's RuntimeContext.
        """
        pass

    def validate_config(self, config: dict) -> dict:
        """
        Validates the configuration against the plugin's schema.
        Returns a dictionary with 'success', 'warnings', and 'errors'.
        """
        return {"success": True, "warnings": [], "errors": []}
