# Copyright (c) 2026 Rudran
# Licensed under the MIT License.

import logging
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.cdk.transform import TransformPlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, LogMessage
from flowcore.engine.exceptions.plugin import RecoverablePluginError
import datetime

logger = logging.getLogger(__name__)

class TypecastTransformPlugin(TransformPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-typecast",
            name="Type Conversion",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Casts columns to specific data types.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"],
            config_schema={
                "type": "object",
                "properties": {
                    "casts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "target_type": {
                                    "type": "string",
                                    "enum": ["string", "integer", "float", "boolean", "date", "datetime"]
                                }
                            },
                            "required": ["column", "target_type"]
                        },
                        "description": "List of columns to cast."
                    },
                    "on_error": {
                        "type": "string",
                        "enum": ["fail", "null"],
                        "default": "fail",
                        "description": "What to do when a cast fails. 'fail' raises an error, 'null' sets the value to null."
                    }
                },
                "required": ["casts"]
            }
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "casts" not in config:
            return False
        return True

    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        casts_list = config.get("casts", [])
        on_error = config.get("on_error", "fail")
        casts = {c["column"]: c["target_type"] for c in casts_list if "column" in c and "target_type" in c}
        
        type_mapping = {
            "string": "string",
            "integer": "integer",
            "float": "number",
            "boolean": "boolean",
            "date": "string",
            "datetime": "string"
        }

        records_received = 0
        records_passed = 0
        records_failed = 0

        for message in message_stream:
            if message.type == MessageType.SCHEMA and message.schema_info:
                # Mutate schema
                props = message.schema_info.schema_data.get("properties", {})
                new_props = {}
                for k, v in props.items():
                    if k in casts:
                        new_props[k] = {"type": type_mapping.get(casts[k], "string")}
                    else:
                        new_props[k] = v
                        
                new_schema_info = message.schema_info.model_copy(update={"schema_data": {**message.schema_info.schema_data, "properties": new_props}})
                yield message.model_copy(update={"schema_info": new_schema_info})
            
            elif message.type == MessageType.RECORD and message.record:
                records_received += 1
                data = message.record.data
                
                new_data = dict(data)
                has_error = False
                
                for col, target_type in casts.items():
                    if col in new_data and new_data[col] is not None:
                        val = new_data[col]
                        try:
                            if target_type == "string":
                                new_data[col] = str(val)
                            elif target_type == "integer":
                                new_data[col] = int(val)
                            elif target_type == "float":
                                new_data[col] = float(val)
                            elif target_type == "boolean":
                                if isinstance(val, str):
                                    new_data[col] = val.lower() in ("true", "1", "t", "yes", "y")
                                else:
                                    new_data[col] = bool(val)
                            elif target_type == "date":
                                if isinstance(val, str):
                                    new_data[col] = datetime.datetime.fromisoformat(val).date().isoformat()
                            elif target_type == "datetime":
                                if isinstance(val, str):
                                    new_data[col] = datetime.datetime.fromisoformat(val).isoformat()
                        except (ValueError, TypeError) as e:
                            has_error = True
                            if on_error == "fail":
                                raise RecoverablePluginError(f"TypeCast failed for column '{col}' with value '{val}' to type '{target_type}'. Record: {records_received}")
                            else:
                                new_data[col] = None
                                
                if has_error and on_error == "null":
                    records_failed += 1 # We consider it a safe failure
                
                new_record = message.record.model_copy(update={"data": new_data})
                records_passed += 1
                yield message.model_copy(update={"record": new_record})
                
            else:
                yield message

        yield FlowCoreMessage(
            type=MessageType.LOG,
            log=LogMessage(level="INFO", message=f"TypeCast metrics: received={records_received}, passed={records_passed}, failed_safe={records_failed}")
        )
