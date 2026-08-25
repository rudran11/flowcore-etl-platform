# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import base64
from typing import Any, Dict, Iterator, Optional
import boto3

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
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

class S3DestinationPlugin(DestinationPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-s3",
            name="Amazon S3 Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Writes objects to Amazon S3.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=True
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
        
    def write(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        client = self._get_client(config)
        bucket = config["bucket"]
        
        # State tracking for multipart uploads
        # dict of name -> {"upload_id": ..., "parts": [...]}
        active_uploads = {}
        
        try:
            for msg in message_stream:
                if msg.type == MessageType.RECORD and msg.record and msg.record.stream == "objects":
                    data = msg.record.data
                    name = data["name"]
                    chunk_index = data["chunk_index"]
                    is_last_chunk = data["is_last_chunk"]
                    content_b64 = data["content_b64"]
                    
                    raw_data = base64.b64decode(content_b64)
                    
                    if name not in active_uploads:
                        res = client.create_multipart_upload(Bucket=bucket, Key=name)
                        active_uploads[name] = {
                            "upload_id": res["UploadId"],
                            "parts": []
                        }
                        
                    upload_id = active_uploads[name]["upload_id"]
                    part_num = chunk_index + 1
                    
                    part_res = client.upload_part(
                        Bucket=bucket,
                        Key=name,
                        PartNumber=part_num,
                        UploadId=upload_id,
                        Body=raw_data
                    )
                    
                    active_uploads[name]["parts"].append({
                        "PartNumber": part_num,
                        "ETag": part_res["ETag"]
                    })
                    
                    if is_last_chunk:
                        client.complete_multipart_upload(
                            Bucket=bucket,
                            Key=name,
                            UploadId=upload_id,
                            MultipartUpload={"Parts": active_uploads[name]["parts"]}
                        )
                        del active_uploads[name]
                        
                elif msg.type == MessageType.STATE:
                    yield msg
                    
        finally:
            # Abort any incomplete multipart uploads
            for name, up_info in active_uploads.items():
                try:
                    client.abort_multipart_upload(
                        Bucket=bucket,
                        Key=name,
                        UploadId=up_info["upload_id"]
                    )
                except Exception:
                    pass
