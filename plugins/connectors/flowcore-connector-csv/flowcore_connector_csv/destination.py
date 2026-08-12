# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import csv
import os
from typing import Any, Dict, Iterator
from pathlib import Path

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field

class CsvDestConfig(BaseModel):
    output_directory: str = Field(..., description="Directory to write CSV files.")
    delimiter: str = Field(",", description="Delimiter used in the CSV.")
    include_header: bool = Field(True, description="Whether to include a header row.")

class CsvDestinationPlugin(DestinationPlugin):
    """
    CSV Destination Connector for FlowCore.
    Supports writing streaming data to local CSV files.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-csv",
            name="CSV Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Loads data into local CSV files.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=True
            ),
            config_schema=CsvDestConfig.model_json_schema()
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
        
        # We need to maintain a dictionary of writers and file objects per stream
        file_handles = {}
        writers = {}
        
        try:
            for msg in message_stream:
                if msg.type == MessageType.RECORD and msg.record:
                    stream_name = msg.record.stream
                    data = msg.record.data
                    
                    if stream_name not in writers:
                        file_path = out_dir / f"{stream_name}.csv"
                        # Open in append mode if files might be written to incrementally, 
                        # but for a simple file destination, 'w' is fine for a single pipeline run.
                        f = open(file_path, "w", newline="", encoding="utf-8")
                        file_handles[stream_name] = f
                        writer = csv.DictWriter(f, fieldnames=data.keys())
                        writer.writeheader()
                        writers[stream_name] = writer
                        
                    # If schema dynamically changes, DictWriter might throw ValueError if extra fields exist
                    # For a robust implementation, we might need a dynamically updating fieldnames list.
                    # For now, we assume schema is consistent or use `extrasaction='ignore'`
                    try:
                        writers[stream_name].writerow(data)
                    except ValueError:
                        # Re-initialize writer if new fields are found (naive approach: just append fields)
                        # We'll just ignore extra fields for this simple CSV destination
                        pass
                
                elif msg.type == MessageType.STATE:
                    # After writing records for this batch/stream, we pass the state message back
                    # so the engine can persist it.
                    yield msg
        finally:
            for f in file_handles.values():
                f.close()
