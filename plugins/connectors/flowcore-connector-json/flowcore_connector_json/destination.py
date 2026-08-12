# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import json
import os
from typing import Any, Dict, Iterator
from pathlib import Path

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field

class JsonDestConfig(BaseModel):
    output_directory: str = Field(..., description="Directory to write JSON files.")

class JsonDestinationPlugin(DestinationPlugin):
    """
    JSONL Destination Connector for FlowCore.
    Supports writing streaming data to local JSON Lines files.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-json",
            name="JSONL Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Loads data into local JSON Lines files.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=True
            ),
            config_schema=JsonDestConfig.model_json_schema()
        )
        
    def check(self, config: Dict[str, Any]) -> bool:
        out_dir = config.get("output_directory")
        if not out_dir:
            raise ValueError("Missing 'output_directory' in config.")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        return True
        
    def write(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        out_dir = Path(config["output_directory"])
        
        file_handles = {}
        
        try:
            for msg in message_stream:
                if msg.type == MessageType.RECORD and msg.record:
                    stream_name = msg.record.stream
                    data = msg.record.data
                    
                    if stream_name not in file_handles:
                        file_path = out_dir / f"{stream_name}.jsonl"
                        f = open(file_path, "w", encoding="utf-8")
                        file_handles[stream_name] = f
                        
                    f = file_handles[stream_name]
                    f.write(json.dumps(data) + "\n")
                
                elif msg.type == MessageType.STATE:
                    yield msg
        finally:
            for f in file_handles.values():
                f.close()
