# Copyright (c) 2026 Rudran
# Licensed under the MIT License.

import logging
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.cdk.transform import TransformPlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, LogMessage

logger = logging.getLogger(__name__)

class RenameTransformPlugin(TransformPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-rename",
            name="Rename Columns",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Renames specific columns in the record.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"],
            config_schema={
                "type": "object",
                "properties": {
                    "mappings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "old_name": {"type": "string"},
                                "new_name": {"type": "string"}
                            },
                            "required": ["old_name", "new_name"]
                        },
                        "description": "List of old and new name mappings."
                    }
                },
                "required": ["mappings"]
            }
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "mappings" not in config:
            return False
        return True

    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        mappings_list = config.get("mappings", [])
        mappings = {m["old_name"]: m["new_name"] for m in mappings_list if "old_name" in m and "new_name" in m}
        
        records_received = 0
        records_passed = 0

        for message in message_stream:
            if message.type == MessageType.SCHEMA and message.schema_info:
                # Mutate schema
                props = message.schema_info.schema_data.get("properties", {})
                new_props = {}
                for k, v in props.items():
                    if k in mappings:
                        new_props[mappings[k]] = v
                    else:
                        new_props[k] = v
                        
                new_schema_info = message.schema_info.model_copy(update={"schema_data": {**message.schema_info.schema_data, "properties": new_props}})
                yield message.model_copy(update={"schema_info": new_schema_info})
            
            elif message.type == MessageType.RECORD and message.record:
                records_received += 1
                data = message.record.data
                
                new_data = {}
                for k, v in data.items():
                    if k in mappings:
                        new_data[mappings[k]] = v
                    else:
                        new_data[k] = v
                        
                new_record = message.record.model_copy(update={"data": new_data})
                records_passed += 1
                yield message.model_copy(update={"record": new_record})
                
            else:
                yield message

        yield FlowCoreMessage(
            type=MessageType.LOG,
            log=LogMessage(level="INFO", message=f"Rename metrics: received={records_received}, passed={records_passed}")
        )
