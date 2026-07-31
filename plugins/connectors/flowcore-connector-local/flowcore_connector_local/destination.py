# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
import base64
from typing import Any, Dict, Iterator

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType

class LocalDestinationPlugin(DestinationPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-local",
            name="Local Filesystem Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Writes files to the local filesystem.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=False
            )
        )
        
    def check(self, config: Dict[str, Any]) -> bool:
        path = config.get("directory")
        if not path:
            raise ValueError("Missing 'directory' in config")
        
        # Ensure it exists or we can create it
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                raise ValueError(f"Could not create directory {path}: {e}")
        return True
        
    def write(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        directory = config["directory"]
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        open_files = {}
        last_modified_map = {}
        
        try:
            for msg in message_stream:
                if msg.type == MessageType.RECORD and msg.record and msg.record.stream == "files":
                    data = msg.record.data
                    name = data["name"]
                    chunk_index = data["chunk_index"]
                    is_last_chunk = data["is_last_chunk"]
                    content_b64 = data["content_b64"]
                    last_modified = data.get("last_modified")
                    
                    target_path = os.path.join(directory, name)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    mode = "wb" if chunk_index == 0 else "ab"
                    
                    if name not in open_files or open_files[name].closed:
                        open_files[name] = open(target_path, mode)
                        
                    open_files[name].write(base64.b64decode(content_b64))
                    
                    if last_modified:
                        last_modified_map[name] = last_modified
                        
                    if is_last_chunk:
                        open_files[name].close()
                        del open_files[name]
                        
                        # Preserve metadata
                        if name in last_modified_map:
                            os.utime(target_path, (last_modified_map[name], last_modified_map[name]))
                            
                elif msg.type == MessageType.STATE:
                    yield msg
        finally:
            for f in open_files.values():
                if not f.closed:
                    f.close()
