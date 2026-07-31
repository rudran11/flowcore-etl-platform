# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import json
import os
from typing import Any, Dict, Iterator, List, Optional
from pathlib import Path

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.schema import infer_schema

class JsonSourcePlugin(SourcePlugin):
    """
    JSON Lines (JSONL) Source Connector for FlowCore.
    Supports reading local JSONL files with streaming and schema discovery.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-json",
            name="JSONL Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts data from local JSON Lines files.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            )
        )
        
    def check(self, config: Dict[str, Any]) -> bool:
        file_path = config.get("file_path")
        if not file_path:
            raise ValueError("Missing 'file_path' in config.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        return True
        
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        file_path = config["file_path"]
        stream_name = Path(file_path).stem
        
        sample_records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for _ in range(100):
                line = f.readline()
                if not line:
                    break
                if line.strip():
                    sample_records.append(json.loads(line))
                    
        schema = infer_schema(sample_records)
        return [{"stream": stream_name, "json_schema": schema}]
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        file_path = config["file_path"]
        stream_name = Path(file_path).stem
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    yield FlowCoreMessage(
                        type=MessageType.RECORD,
                        record=RecordMessage(stream=stream_name, data=data)
                    )
