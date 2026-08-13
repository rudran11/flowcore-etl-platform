# Copyright (c) 2026 Rudran
# Licensed under the MIT License.

import logging
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.cdk.transform import TransformPlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, LogMessage
from flowcore.engine.exceptions.plugin import RecoverablePluginError

try:
    from simpleeval import simple_eval
except ImportError:
    simple_eval = None

logger = logging.getLogger(__name__)

class DeriveTransformPlugin(TransformPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-derive",
            name="Derived Column",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Derives a new column using a safe mathematical/string expression.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"],
            config_schema={
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "Name of the new derived column."
                    },
                    "expression": {
                        "type": "string",
                        "description": "Expression to evaluate, e.g., 'amount * quantity' or 'first_name + \" \" + last_name'."
                    },
                    "on_error": {
                        "type": "string",
                        "enum": ["fail", "null"],
                        "default": "fail",
                        "description": "What to do when evaluation fails."
                    }
                },
                "required": ["column", "expression"]
            }
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "column" not in config or "expression" not in config:
            return False
        if simple_eval is None:
            logger.warning("simpleeval is not installed. Derive plugin will fail at runtime.")
        return True

    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        if simple_eval is None:
            raise RuntimeError("simpleeval is required for transform-derive but is not installed.")

        column = config.get("column")
        expression = config.get("expression")
        on_error = config.get("on_error", "fail")
        
        records_received = 0
        records_passed = 0
        records_failed = 0

        for message in message_stream:
            if message.type == MessageType.SCHEMA and message.schema_info:
                # Mutate schema (default to string since we don't know the eval output type statically)
                props = message.schema_info.schema_data.get("properties", {})
                props[column] = {"type": "string"}
                new_schema_info = message.schema_info.model_copy(update={"schema_data": {**message.schema_info.schema_data, "properties": props}})
                yield message.model_copy(update={"schema_info": new_schema_info})
            
            elif message.type == MessageType.RECORD and message.record:
                records_received += 1
                data = message.record.data
                
                new_data = dict(data)
                
                try:
                    # names=new_data makes all record fields available as variables in the expression!
                    result = simple_eval(expression, names=new_data)
                    new_data[column] = result
                except Exception as e:
                    if on_error == "fail":
                        raise RecoverablePluginError(f"Derive failed for column '{column}' with expression '{expression}': {e}. Record: {records_received}")
                    else:
                        new_data[column] = None
                        records_failed += 1
                
                new_record = message.record.model_copy(update={"data": new_data})
                records_passed += 1
                yield message.model_copy(update={"record": new_record})
                
            else:
                yield message

        yield FlowCoreMessage(
            type=MessageType.LOG,
            log=LogMessage(level="INFO", message=f"Derive metrics: received={records_received}, passed={records_passed}, failed_safe={records_failed}")
        )
