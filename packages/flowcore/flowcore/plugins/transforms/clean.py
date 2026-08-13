# Copyright (c) 2026 Rudran
# Licensed under the MIT License.

import logging
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.cdk.transform import TransformPlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, LogMessage

logger = logging.getLogger(__name__)

class CleanTransformPlugin(TransformPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-clean",
            name="Data Cleaning",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Performs common data cleaning operations like trim, lowercase, or null replacement.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"],
            config_schema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "operation": {
                                    "type": "string",
                                    "enum": ["trim_whitespace", "lowercase", "uppercase", "replace_null", "empty_to_null"]
                                },
                                "args": {
                                    "type": "string",
                                    "description": "Additional argument, e.g., the replacement value for replace_null."
                                }
                            },
                            "required": ["column", "operation"]
                        },
                        "description": "List of cleaning operations to apply."
                    }
                },
                "required": ["operations"]
            }
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "operations" not in config:
            return False
        return True

    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        operations = config.get("operations", [])
        
        records_received = 0
        records_passed = 0

        for message in message_stream:
            if message.type == MessageType.SCHEMA:
                # Cleaning operations usually do not mutate the overall schema structure.
                yield message
            
            elif message.type == MessageType.RECORD and message.record:
                records_received += 1
                data = message.record.data
                
                new_data = dict(data)
                
                for op_def in operations:
                    col = op_def.get("column")
                    op = op_def.get("operation")
                    args = op_def.get("args")
                    
                    if col in new_data:
                        val = new_data[col]
                        
                        if op == "trim_whitespace" and isinstance(val, str):
                            new_data[col] = val.strip()
                        elif op == "lowercase" and isinstance(val, str):
                            new_data[col] = val.lower()
                        elif op == "uppercase" and isinstance(val, str):
                            new_data[col] = val.upper()
                        elif op == "empty_to_null" and isinstance(val, str):
                            if val.strip() == "":
                                new_data[col] = None
                        elif op == "replace_null" and val is None:
                            new_data[col] = args
                
                new_record = message.record.model_copy(update={"data": new_data})
                records_passed += 1
                yield message.model_copy(update={"record": new_record})
                
            else:
                yield message

        yield FlowCoreMessage(
            type=MessageType.LOG,
            log=LogMessage(level="INFO", message=f"Clean metrics: received={records_received}, passed={records_passed}")
        )
