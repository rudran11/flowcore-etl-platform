import pytest
from flowcore.plugins.transforms.rename import RenameTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

def test_rename_plugin():
    plugin = RenameTransformPlugin()
    config = {
        "mappings": [
            {"old_name": "id", "new_name": "user_id"},
            {"old_name": "name", "new_name": "full_name"}
        ]
    }

    # 1. Test Schema Mutation
    schema_msg = FlowCoreMessage(
        type=MessageType.SCHEMA,
        schema_info=SchemaMessage(
            stream="test_stream",
            schema_data={"properties": {"id": {"type": "string"}, "name": {"type": "string"}, "age": {"type": "integer"}}}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([schema_msg])))
    assert len(result_msgs) == 2
    out_schema = result_msgs[0]
    assert out_schema.type == MessageType.SCHEMA
    assert "id" not in out_schema.schema_info.schema_data["properties"]
    assert "name" not in out_schema.schema_info.schema_data["properties"]
    assert "user_id" in out_schema.schema_info.schema_data["properties"]
    assert "full_name" in out_schema.schema_info.schema_data["properties"]
    assert "age" in out_schema.schema_info.schema_data["properties"]

    # 2. Test Record Transformation
    record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"id": "1", "name": "rudran", "age": 25}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([record_msg])))
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert "id" not in out_record.record.data
    assert "name" not in out_record.record.data
    assert out_record.record.data["user_id"] == "1"
    assert out_record.record.data["full_name"] == "rudran"
    assert out_record.record.data["age"] == 25
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=1, passed=1" in log_msg.log.message
