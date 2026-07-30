# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import abstractmethod
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.base import BasePlugin
from .messages import FlowCoreMessage

class TransformPlugin(BasePlugin):
    """
    Abstract base class for all Transformer plugins.
    """
    
    def execute(self, context: Any) -> Any:
        """
        Main execution entrypoint called by the engine.
        For transformers, this routes to transform().
        """
        config = context.get("config", {})
        message_stream = context.get("message_stream", iter([]))
        catalog = context.get("catalog", None)
        return self.transform(config, catalog, message_stream)
        
    @abstractmethod
    def check(self, config: Dict[str, Any]) -> bool:
        """
        Validates the configuration.
        """
        pass
        
    @abstractmethod
    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        """
        Consumes the generator of FlowCoreMessage objects, applies transformations,
        and yields the transformed messages.
        """
        pass
