# Copyright (c) 2026 Rudran
# Licensed under the MIT License.

import logging
from typing import Any, Dict, Iterator
from flowcore_shared.plugins.cdk.transform import TransformPlugin
from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, LogMessage

logger = logging.getLogger(__name__)

class FilterTransformPlugin(TransformPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-filter",
            name="Filter Rows",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Filters records based on simple conditions.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"],
            config_schema={
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "description": "List of conditions to match. A record must pass all conditions.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string"},
                                "operator": {
                                    "type": "string",
                                    "enum": ["==", "!=", ">", "<", ">=", "<=", "IN"]
                                },
                                "value": {"type": "string"}
                            },
                            "required": ["field", "operator", "value"]
                        }
                    }
                },
                "required": ["conditions"]
            }
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if "conditions" not in config:
            return False
        return True

    def transform(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        raw_conditions = config.get("conditions", [])
        conditions = []
        
        print(f"[FILTER DEBUG] raw_conditions={raw_conditions} type={type(raw_conditions)}")
        
        if isinstance(raw_conditions, str):
            # Parse simple string condition like "amount > 60"
            import re
            match = re.match(r'^\s*([a-zA-Z0-9_]+)\s*(==|!=|>|<|>=|<=|IN)\s*(.*)\s*$', raw_conditions)
            if match:
                conditions.append({
                    "field": match.group(1),
                    "operator": match.group(2),
                    "value": match.group(3).strip()
                })
        elif isinstance(raw_conditions, list):
            for c in raw_conditions:
                if isinstance(c, dict):
                    conditions.append(c)
                elif isinstance(c, str):
                    import re
                    match = re.match(r'^\s*([a-zA-Z0-9_]+)\s*(==|!=|>|<|>=|<=|IN)\s*(.*)\s*$', c)
                    if match:
                        conditions.append({
                            "field": match.group(1),
                            "operator": match.group(2),
                            "value": match.group(3).strip()
                        })
        
        records_received = 0
        records_passed = 0
        records_filtered = 0

        for message in message_stream:
            if message.type == MessageType.SCHEMA:
                yield message
            
            elif message.type == MessageType.RECORD and message.record:
                records_received += 1
                data = message.record.data
                
                passed = True
                for cond in conditions:
                    field = cond.get("field")
                    op = cond.get("operator")
                    val = cond.get("value")
                    
                    if field not in data:
                        passed = False
                        break
                        
                    actual_val = data[field]
                    
                    try:
                        if isinstance(actual_val, int) and isinstance(val, str) and val.isdigit():
                            val = int(val)
                        elif isinstance(actual_val, float) and isinstance(val, str):
                            val = float(val)
                    except ValueError:
                        pass

                    try:
                        if op == "==":
                            if actual_val != val: passed = False
                        elif op == "!=":
                            if actual_val == val: passed = False
                        elif op == ">":
                            if not (actual_val > val): passed = False
                        elif op == "<":
                            if not (actual_val < val): passed = False
                        elif op == ">=":
                            if not (actual_val >= val): passed = False
                        elif op == "<=":
                            if not (actual_val <= val): passed = False
                        elif op == "IN":
                            if isinstance(val, str):
                                val_list = [v.strip() for v in val.split(",")]
                                if str(actual_val) not in val_list: passed = False
                    except TypeError:
                        # Incompatible types for comparison
                        passed = False
                    
                    print(f"[FILTER DEBUG] actual_val={actual_val} type={type(actual_val)}, op={op}, val={val} type={type(val)} -> passed={passed}")
                    
                    if not passed:
                        break
                
                if passed:
                    records_passed += 1
                    yield message
                else:
                    records_filtered += 1
                    
            elif message.type == MessageType.STATE:
                yield message
                
            elif message.type == MessageType.LOG:
                yield message

        yield FlowCoreMessage(
            type=MessageType.LOG,
            log=LogMessage(level="INFO", message=f"Filter metrics: received={records_received}, passed={records_passed}, filtered={records_filtered}")
        )
