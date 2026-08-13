import pytest
from flowcore.plugins.transforms.select import SelectTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

def test_select_plugin():
    plugin = SelectTransformPlugin()
    config = {
        "columns": ["id", "name"]
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
    assert "age" not in out_schema.schema_info.schema_data["properties"]
    assert "id" in out_schema.schema_info.schema_data["properties"]
    assert "name" in out_schema.schema_info.schema_data["properties"]

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
    assert "age" not in out_record.record.data
    assert out_record.record.data["id"] == "1"
    assert out_record.record.data["name"] == "rudran"
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=1, passed=1" in log_msg.log.message
