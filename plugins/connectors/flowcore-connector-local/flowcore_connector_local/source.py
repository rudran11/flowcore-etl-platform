# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
import glob
import base64
from typing import Any, Dict, Iterator, List, Optional

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field

class LocalSourceConfig(BaseModel):
    directory_path: str = Field(..., description="Path to the local directory.")

class LocalSourcePlugin(SourcePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-local",
            name="Local Filesystem Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts files from the local filesystem.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=True,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            ),
            config_schema=LocalSourceConfig.model_json_schema()
        )
        
    def check(self, config: Dict[str, Any]) -> bool:
        path = config.get("directory")
        if not path:
            raise ValueError("Missing 'directory' in config")
        if not os.path.exists(path) or not os.path.isdir(path):
            raise ValueError(f"Directory {path} does not exist or is not a directory.")
        return True
        
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Schema for a chunked file stream
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "size_bytes": {"type": "integer"},
                "last_modified": {"type": "number"},
                "chunk_index": {"type": "integer"},
                "is_last_chunk": {"type": "boolean"},
                "content_b64": {"type": "string"}
            }
        }
        return [{"stream": "files", "json_schema": schema}]
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        directory = config["directory"]
        recursive = config.get("recursive", True)
        chunk_size = config.get("chunk_size", 1024 * 1024) # 1MB chunks
        
        # Incremental sync uses last_modified as the replication key
        cursor_value = 0.0
        if state and "files" in state:
            cursor_value = state["files"].get("last_modified", 0.0)
            
        max_cursor = cursor_value
        
        pattern = os.path.join(directory, "**", "*") if recursive else os.path.join(directory, "*")
        
        for file_path in glob.iglob(pattern, recursive=recursive):
            if not os.path.isfile(file_path):
                continue
                
            stat = os.stat(file_path)
            last_modified = stat.st_mtime
            
            if last_modified <= cursor_value:
                continue
                
            # Stream the file in chunks
            with open(file_path, "rb") as f:
                chunk_index = 0
                while True:
                    data = f.read(chunk_size)
                    is_last_chunk = len(data) < chunk_size
                    
                    record = {
                        "name": os.path.relpath(file_path, directory),
                        "size_bytes": stat.st_size,
                        "last_modified": last_modified,
                        "chunk_index": chunk_index,
                        "is_last_chunk": is_last_chunk,
                        "content_b64": base64.b64encode(data).decode("utf-8")
                    }
                    
                    yield FlowCoreMessage(
                        type=MessageType.RECORD,
                        record=RecordMessage(stream="files", data=record)
                    )
                    
                    if is_last_chunk:
                        break
                        
                    chunk_index += 1
                    
            if last_modified > max_cursor:
                max_cursor = last_modified
                
        # Emit state at the end
        if max_cursor > cursor_value:
            yield FlowCoreMessage(
                type=MessageType.STATE,
                state=StateMessage(state_data={"files": {"last_modified": max_cursor}})
            )
