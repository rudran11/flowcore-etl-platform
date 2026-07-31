from typing import Any, Dict, Iterator, List, Optional
from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType

class MyCustomSourcePlugin(SourcePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="my-custom-source",
            name="my-custom-source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="Your Name",
            description="Scaffolded Source Plugin",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities()
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "api_key" not in config:
            raise ValueError("Missing api_key")
        return True

    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"stream": "default_stream", "json_schema": {"type": "object"}}]

    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        last_id = state.get("last_id", 0) if state else 0

        # Example implementation: yield 5 records
        for i in range(1, 6):
            current_id = last_id + i
            yield FlowCoreMessage(
                type=MessageType.RECORD,
                record=RecordMessage(stream="default_stream", data={"id": current_id, "value": "test"})
            )
            yield FlowCoreMessage(
                type=MessageType.STATE,
                state=StateMessage(state_data={"last_id": current_id})
            )
