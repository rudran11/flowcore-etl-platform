# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import abstractmethod
from typing import Any, Dict, Iterator, List, Optional
from flowcore_shared.plugins.base import BasePlugin
from .messages import FlowCoreMessage

class SourcePlugin(BasePlugin):
    """
    Abstract base class for all Extractor (Source) plugins.
    """
    
    def execute(self, context: Any) -> Any:
        """
        Main execution entrypoint called by the engine.
        For sources, this typically routes to read().
        """
        config = context.get("config", {})
        state = context.get("state", {})
        catalog = context.get("catalog", None)
        return self.read(config, catalog, state)
        
    @abstractmethod
    def check(self, config: Dict[str, Any]) -> bool:
        """
        Validates the configuration and checks connection to the source.
        Returns True if successful, raises ConnectionError or ConfigError otherwise.
        """
        pass
        
    @abstractmethod
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Discovers the available streams and their schemas.
        Returns a list of stream catalogs.
        """
        pass
        
    @abstractmethod
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        """
        Reads data from the source and yields a stream of FlowCoreMessage objects.
        """
        pass
