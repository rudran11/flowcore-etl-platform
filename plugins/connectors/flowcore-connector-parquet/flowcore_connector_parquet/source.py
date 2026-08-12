# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
from typing import Any, Dict, Iterator, List, Optional
from pathlib import Path

import pyarrow.parquet as pq

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.schema import infer_schema

class ParquetSourceConfig(BaseModel):
    file_path: str = Field(..., description="Path to the Parquet file or directory.")

class ParquetSourcePlugin(SourcePlugin):
    """
    Parquet Source Connector for FlowCore.
    Supports reading local Parquet files via pyarrow for streaming.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-parquet",
            name="Parquet Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts data from local Parquet files.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            ),
            config_schema=ParquetSourceConfig.model_json_schema()
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
        
        # Read the first row group to infer schema
        parquet_file = pq.ParquetFile(file_path)
        if parquet_file.num_row_groups == 0:
            return [{"stream": stream_name, "json_schema": {"type": "object", "properties": {}}}]
            
        first_batch = parquet_file.read_row_group(0).to_pylist()
        sample = first_batch[:100]
        schema = infer_schema(sample)
        
        return [{"stream": stream_name, "json_schema": schema}]
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        file_path = config["file_path"]
        stream_name = Path(file_path).stem
        
        parquet_file = pq.ParquetFile(file_path)
        for i in range(parquet_file.num_row_groups):
            batch = parquet_file.read_row_group(i).to_pylist()
            for row in batch:
                yield FlowCoreMessage(
                    type=MessageType.RECORD,
                    record=RecordMessage(stream=stream_name, data=row)
                )
