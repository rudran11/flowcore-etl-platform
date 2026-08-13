import pytest
from flowcore.plugins.transforms.clean import CleanTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

def test_clean_plugin():
    plugin = CleanTransformPlugin()
    config = {
        "operations": [
            {"column": "name", "operation": "trim_whitespace"},
            {"column": "name", "operation": "lowercase"},
            {"column": "email", "operation": "trim_whitespace"},
            {"column": "email", "operation": "lowercase"},
            {"column": "name", "operation": "replace_null", "args": ""},
            {"column": "email", "operation": "replace_null", "args": ""}
        ]
    }

    # 1. Test Schema Mutation (should be pass-through)
    schema_msg = FlowCoreMessage(
        type=MessageType.SCHEMA,
        schema_info=SchemaMessage(
            stream="test_stream",
            schema_data={"properties": {"name": {"type": "string"}, "email": {"type": "string"}}}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([schema_msg])))
    assert len(result_msgs) == 2
    out_schema = result_msgs[0]
    assert out_schema.type == MessageType.SCHEMA
    assert out_schema.schema_info.schema_data == schema_msg.schema_info.schema_data

    # 2. Test Record Transformation
    record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={
                "name": "  RUDRAN  ",
                "email": " Rudran@Example.com ",
                "age": 25,
                "other": None
            }
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([record_msg])))
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert out_record.record.data["name"] == "rudran"
    assert out_record.record.data["email"] == "rudran@example.com"
    assert out_record.record.data["age"] == 25
    assert out_record.record.data["other"] is None

    # Test replace_null
    record_msg2 = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={
                "name": None,
                "email": None
            }
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([record_msg2])))
    out_record = result_msgs[0]
    assert out_record.record.data["name"] == ""
    assert out_record.record.data["email"] == ""
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=1, passed=1" in log_msg.log.message
