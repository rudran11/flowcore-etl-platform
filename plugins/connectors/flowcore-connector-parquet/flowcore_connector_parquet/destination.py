# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
from typing import Any, Dict, Iterator
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field

class ParquetDestConfig(BaseModel):
    output_directory: str = Field(..., description="Directory to write Parquet files.")

class ParquetDestinationPlugin(DestinationPlugin):
    """
    Parquet Destination Connector for FlowCore.
    Supports writing streaming data to local Parquet files in batches.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-parquet",
            name="Parquet Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Loads data into local Parquet files.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=True
            ),
            config_schema=ParquetDestConfig.model_json_schema()
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
        batch_size = config.get("batch_size", 1000)
        
        writers = {}
        buffers = {}
        schemas = {}
        
        try:
            for msg in message_stream:
                if msg.type == MessageType.RECORD and msg.record:
                    stream_name = msg.record.stream
                    data = msg.record.data
                    
                    if stream_name not in buffers:
                        buffers[stream_name] = []
                        
                    buffers[stream_name].append(data)
                    
                    if len(buffers[stream_name]) >= batch_size:
                        self._flush_buffer(stream_name, buffers, schemas, writers, out_dir)
                
                elif msg.type == MessageType.STATE:
                    yield msg
                    
            # Flush remaining
            for stream_name in list(buffers.keys()):
                if buffers[stream_name]:
                    self._flush_buffer(stream_name, buffers, schemas, writers, out_dir)
                    
        finally:
            for writer in writers.values():
                writer.close()
                
    def _flush_buffer(self, stream_name: str, buffers: Dict, schemas: Dict, writers: Dict, out_dir: Path):
        data_list = buffers[stream_name]
        
        # Convert list of dicts to PyArrow Table
        # Using from_pylist infers the PyArrow schema automatically
        table = pa.Table.from_pylist(data_list)
        
        if stream_name not in writers:
            schemas[stream_name] = table.schema
            file_path = out_dir / f"{stream_name}.parquet"
            writers[stream_name] = pq.ParquetWriter(file_path, table.schema)
            
        writers[stream_name].write_table(table)
        buffers[stream_name].clear()
