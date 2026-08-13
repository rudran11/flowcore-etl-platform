# Copyright (c) 2026 Rudran
# Licensed under the MIT License.

import logging
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.cdk.transform import TransformPlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, LogMessage

logger = logging.getLogger(__name__)

class SelectTransformPlugin(TransformPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-select",
            name="Select Columns",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Selects or drops specific columns from the record.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"],
            config_schema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["keep", "drop"],
                        "default": "keep",
                        "description": "Whether to keep only the specified columns, or drop them."
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of column names."
                    }
                },
                "required": ["mode", "columns"]
            }
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "columns" not in config:
            return False
        return True

    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        mode = config.get("mode", "keep")
        columns = set(config.get("columns", []))
        
        records_received = 0
        records_passed = 0

        for message in message_stream:
            if message.type == MessageType.SCHEMA and message.schema_info:
                # Mutate schema
                props = message.schema_info.schema_data.get("properties", {})
                new_props = {}
                for k, v in props.items():
                    if mode == "keep" and k in columns:
                        new_props[k] = v
                    elif mode == "drop" and k not in columns:
                        new_props[k] = v
                        
                new_schema_info = message.schema_info.model_copy(update={"schema_data": {**message.schema_info.schema_data, "properties": new_props}})
                yield message.model_copy(update={"schema_info": new_schema_info})
            
            elif message.type == MessageType.RECORD and message.record:
                records_received += 1
                data = message.record.data
                
                new_data = {}
                for k, v in data.items():
                    if mode == "keep" and k in columns:
                        new_data[k] = v
                    elif mode == "drop" and k not in columns:
                        new_data[k] = v
                        
                new_record = message.record.model_copy(update={"data": new_data})
                records_passed += 1
                yield message.model_copy(update={"record": new_record})
                
            else:
                yield message

        yield FlowCoreMessage(
            type=MessageType.LOG,
            log=LogMessage(level="INFO", message=f"Select metrics: received={records_received}, passed={records_passed}")
        )
