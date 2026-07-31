import base64
import pytest
import sys
from unittest.mock import MagicMock, patch

# Inject a mock boto3 into sys.modules so imports succeed without installing boto3
mock_boto3 = MagicMock()
sys.modules['boto3'] = mock_boto3

from flowcore_connector_s3.source import S3SourcePlugin
from flowcore_connector_s3.destination import S3DestinationPlugin
from flowcore_shared.plugins.cdk.messages import MessageType, RecordMessage, StateMessage, FlowCoreMessage

@patch("boto3.client")
def test_s3_source(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    
    # Mock head_bucket
    mock_client.head_bucket.return_value = {}
    
    # Mock pagination
    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator
    
    mock_paginator.paginate.return_value = [
        {
            "Contents": [
                {"Key": "test1.txt", "LastModified": MagicMock(timestamp=lambda: 1000.0), "Size": 10},
            ]
        }
    ]
    
    # Mock get_object
    mock_body = MagicMock()
    mock_body.read.side_effect = [b"Hello ", b"World!", b""]
    mock_client.get_object.return_value = {"Body": mock_body}
    
    source = S3SourcePlugin()
    config = {"bucket": "test-bucket", "chunk_size": 6}
    
    assert source.check(config)
    
    messages = list(source.read(config))
    records = [m for m in messages if m.type == MessageType.RECORD]
    states = [m for m in messages if m.type == MessageType.STATE]
    
    assert len(records) == 3
    assert len(states) == 1
    
    assert records[0].record.data["content_b64"] == base64.b64encode(b"Hello ").decode("utf-8")
    assert records[1].record.data["content_b64"] == base64.b64encode(b"World!").decode("utf-8")
    
@patch("boto3.client")
def test_s3_destination(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    
    mock_client.create_multipart_upload.return_value = {"UploadId": "up123"}
    mock_client.upload_part.return_value = {"ETag": "etag123"}
    
    dest = S3DestinationPlugin()
    config = {"bucket": "test-bucket"}
    
    messages = [
        FlowCoreMessage(
            type=MessageType.RECORD,
            record=RecordMessage(
                stream="objects",
                data={
                    "name": "test1.txt",
                    "chunk_index": 0,
                    "is_last_chunk": False,
                    "content_b64": base64.b64encode(b"Hello ").decode("utf-8")
                }
            )
        ),
        FlowCoreMessage(
            type=MessageType.RECORD,
            record=RecordMessage(
                stream="objects",
                data={
                    "name": "test1.txt",
                    "chunk_index": 1,
                    "is_last_chunk": True,
                    "content_b64": base64.b64encode(b"World!").decode("utf-8")
                }
            )
        )
    ]
    
    # write modifies in place but consumes the stream
    list(dest.write(config, None, iter(messages)))
    
    assert mock_client.create_multipart_upload.call_count == 1
    assert mock_client.upload_part.call_count == 2
    assert mock_client.complete_multipart_upload.call_count == 1
