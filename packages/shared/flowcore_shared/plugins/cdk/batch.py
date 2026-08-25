# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import abstractmethod
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.base import BasePlugin
from .messages import FlowCoreMessage

class BatchTransformPlugin(BasePlugin):
    """
    Abstract base class for stateful/dataset-level Transformers.
    Unlike TransformPlugin which consumes row-by-row statelessly,
    BatchTransformPlugin reads the entire bounded input stream,
    performs stateful operations (like Aggregate, Sort, Deduplicate)
    and yields the output stream.
    """
    
    def execute(self, context: Any) -> Any:
        """
        Main execution entrypoint called by the engine.
        """
        config = getattr(context, "parameters", {})
        message_stream = getattr(context, "message_stream", iter([]))
        catalog = getattr(context, "catalog", None)
        return self.transform_batch(config, catalog, message_stream, context)
        
    @abstractmethod
    def check(self, config: Dict[str, Any]) -> bool:
        """
        Validates the configuration.
        """
        pass
        
    @abstractmethod
    def transform_batch(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage], context: Any) -> Iterator[FlowCoreMessage]:
        """
        Consumes the incoming generator entirely, performs batch processing,
        and yields the transformed messages.
        """
        pass


class MultiInputTransformPlugin(BasePlugin):
    """
    Abstract base class for Multi-Input Transformers (like Join).
    Consumes multiple upstream message streams.
    """
    
    def execute(self, context: Any) -> Any:
        """
        Main execution entrypoint called by the engine.
        """
        config = getattr(context, "parameters", {})
        message_streams = getattr(context, "message_streams", {})
        catalog = getattr(context, "catalog", None)
        return self.transform_multi(config, catalog, message_streams, context)
        
    @abstractmethod
    def check(self, config: Dict[str, Any]) -> bool:
        """
        Validates the configuration.
        """
        pass
        
    @abstractmethod
    def transform_multi(self, config: Dict[str, Any], catalog: Any, message_streams: Dict[str, Iterator[FlowCoreMessage]], context: Any) -> Iterator[FlowCoreMessage]:
        """
        Consumes multiple incoming generators, performs multi-input processing (e.g. Join),
        and yields the transformed messages.
        """
        pass
