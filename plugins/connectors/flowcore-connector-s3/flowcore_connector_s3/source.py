# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import base64
from typing import Any, Dict, Iterator, List, Optional
import boto3

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field, SecretStr

class S3Config(BaseModel):
    bucket: str = Field(..., description="Amazon S3 bucket name.")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID.")
    aws_secret_access_key: Optional[SecretStr] = Field(None, description="AWS Secret Access Key.")
    region_name: str = Field("us-east-1", description="AWS Region name.")
    endpoint_url: Optional[str] = Field(None, description="Custom endpoint URL (e.g., for MinIO).")
    prefix: Optional[str] = Field(None, description="S3 Key prefix.")

class S3SourcePlugin(SourcePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-s3",
            name="Amazon S3 Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts objects from Amazon S3.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=True,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            ),
            config_schema=S3Config.model_json_schema()
        )
        
    def _get_client(self, config: Dict[str, Any]):
        return boto3.client(
            's3',
            aws_access_key_id=config.get("aws_access_key_id"),
            aws_secret_access_key=config.get("aws_secret_access_key"),
            region_name=config.get("region_name", "us-east-1"),
            endpoint_url=config.get("endpoint_url")
        )

    def check(self, config: Dict[str, Any]) -> bool:
        if not config.get("bucket"):
            raise ValueError("Missing 'bucket' in config")
        
        client = self._get_client(config)
        client.head_bucket(Bucket=config["bucket"])
        return True
        
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
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
        return [{"stream": "objects", "json_schema": schema}]
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        client = self._get_client(config)
        bucket = config["bucket"]
        prefix = config.get("prefix", "")
        chunk_size = config.get("chunk_size", 5 * 1024 * 1024) # 5MB chunks
        
        cursor_value = 0.0
        if state and "objects" in state:
            cursor_value = state["objects"].get("last_modified", 0.0)
            
        max_cursor = cursor_value
        
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        
        for page in pages:
            if "Contents" not in page:
                continue
                
            for obj in page["Contents"]:
                key = obj["Key"]
                last_modified = obj["LastModified"].timestamp()
                size = obj["Size"]
                
                if last_modified <= cursor_value:
                    continue
                    
                response = client.get_object(Bucket=bucket, Key=key)
                body = response['Body']
                
                chunk_index = 0
                while True:
                    data = body.read(chunk_size)
                    is_last_chunk = len(data) < chunk_size
                    
                    record = {
                        "name": key,
                        "size_bytes": size,
                        "last_modified": last_modified,
                        "chunk_index": chunk_index,
                        "is_last_chunk": is_last_chunk,
                        "content_b64": base64.b64encode(data).decode("utf-8")
                    }
                    
                    yield FlowCoreMessage(
                        type=MessageType.RECORD,
                        record=RecordMessage(stream="objects", data=record)
                    )
                    
                    if is_last_chunk:
                        break
                        
                    chunk_index += 1
                    
                if last_modified > max_cursor:
                    max_cursor = last_modified
                    
        if max_cursor > cursor_value:
            yield FlowCoreMessage(
                type=MessageType.STATE,
                state=StateMessage(state_data={"objects": {"last_modified": max_cursor}})
            )
