from typing import Any, Dict, Iterator
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage

class TestSourcePlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="test-source",
            name="Test Source",
            version="1.0.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore",
            description="Mock source",
            category="Test",
            capabilities=ConnectorCapabilities(),
            supported_operations=["extract"],
            config_schema={}
        )

    def execute(self, context: Any) -> Iterator[FlowCoreMessage]:
        yield FlowCoreMessage(
            type=MessageType.SCHEMA,
            schema_info=SchemaMessage(
                stream="orders",
                schema_data={
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "customer_id": {"type": "string"},
                        "amount": {"type": "number"},
                        "status": {"type": "string"}
                    }
                }
            )
        )
        if context.preview_context.cancellation_event.is_set():
            return
            
        yield FlowCoreMessage(
            type=MessageType.RECORD,
            record=RecordMessage(
                stream="orders",
                data={"order_id": "O1", "customer_id": " C1 ", "amount": 100, "status": "COMPLETED"}
            )
        )
        if context.preview_context.cancellation_event.is_set():
            return
            
        yield FlowCoreMessage(
            type=MessageType.RECORD,
            record=RecordMessage(
                stream="orders",
                data={"order_id": "O2", "customer_id": " C2 ", "amount": 50, "status": "PENDING"}
            )
        )
        if context.preview_context.cancellation_event.is_set():
            return
            
        yield FlowCoreMessage(
            type=MessageType.RECORD,
            record=RecordMessage(
                stream="orders",
                data={"order_id": "O3", "customer_id": " C1 ", "amount": 200, "status": "COMPLETED"}
            )
        )
