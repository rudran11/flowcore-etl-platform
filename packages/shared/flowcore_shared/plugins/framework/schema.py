# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Any, Dict, List

def infer_schema(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Infers a basic JSON Schema from a list of records.
    """
    if not records:
        return {"type": "object", "properties": {}}

    properties = {}
    for record in records:
        for key, value in record.items():
            if key not in properties:
                if isinstance(value, bool):
                    properties[key] = {"type": "boolean"}
                elif isinstance(value, int):
                    properties[key] = {"type": "integer"}
                elif isinstance(value, float):
                    properties[key] = {"type": "number"}
                elif isinstance(value, str):
                    properties[key] = {"type": "string"}
                elif isinstance(value, dict):
                    properties[key] = {"type": "object"}
                elif isinstance(value, list):
                    properties[key] = {"type": "array"}
                elif value is None:
                    # Can't infer type from None, skip for now
                    pass
                else:
                    properties[key] = {"type": "string"} # Default to string for unknown types

    return {
        "type": "object",
        "properties": properties
    }
