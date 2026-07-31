# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import abstractmethod
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.base import BasePlugin
from .messages import FlowCoreMessage

class DestinationPlugin(BasePlugin):
    """
    Abstract base class for all Loader (Destination) plugins.
    """
    
    def execute(self, context: Any) -> Any:
        """
        Main execution entrypoint called by the engine.
        For destinations, this routes to write().
        """
        config = getattr(context, "parameters", {})
        message_stream = getattr(context, "message_stream", iter([]))
        catalog = getattr(context, "catalog", None)
        return self.write(config, catalog, message_stream)
        
    @abstractmethod
    def check(self, config: Dict[str, Any]) -> bool:
        """
        Validates the configuration and checks connection to the destination.
        Returns True if successful, raises ConnectionError or ConfigError otherwise.
        """
        pass
        
    @abstractmethod
    def write(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        """
        Consumes the generator of FlowCoreMessage objects, writes them to the destination,
        and yields state/log messages back to the engine.
        """
        pass
