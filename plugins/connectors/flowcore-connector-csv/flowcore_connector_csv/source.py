# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import csv
import os
from typing import Any, Dict, Iterator, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.schema import infer_schema

class CsvSourceConfig(BaseModel):
    file_path: str = Field(..., description="Path to the CSV file.")
    delimiter: str = Field(",", description="Delimiter used in the CSV.")
    has_header: bool = Field(True, description="Whether the CSV has a header row.")

class CsvSourcePlugin(SourcePlugin):
    """
    CSV Source Connector for FlowCore.
    Supports reading local CSV files with streaming and schema discovery.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-csv",
            name="CSV Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts data from local CSV files.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            ),
            config_schema=CsvSourceConfig.model_json_schema()
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
        
        # Read a small sample to infer schema
        sample_records = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for _ in range(100):
                try:
                    row = next(reader)
                    sample_records.append(row)
                except StopIteration:
                    break
                    
        schema = infer_schema(sample_records)
        return [{"stream": stream_name, "json_schema": schema}]
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        file_path = config["file_path"]
        stream_name = Path(file_path).stem
        
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                yield FlowCoreMessage(
                    type=MessageType.RECORD,
                    record=RecordMessage(stream=stream_name, data=row)
                )
