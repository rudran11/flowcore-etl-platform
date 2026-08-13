import pytest
from flowcore.plugins.transforms.typecast import TypecastTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

def test_typecast_plugin():
    plugin = TypecastTransformPlugin()
    config = {
        "casts": [
            {"column": "age", "target_type": "integer"},
            {"column": "score", "target_type": "float"},
            {"column": "is_active", "target_type": "boolean"},
            {"column": "date_str", "target_type": "date"}
        ],
        "on_error": "null"
    }

    # 1. Test Schema Mutation
    schema_msg = FlowCoreMessage(
        type=MessageType.SCHEMA,
        schema_info=SchemaMessage(
            stream="test_stream",
            schema_data={"properties": {"age": {"type": "string"}, "name": {"type": "string"}}}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([schema_msg])))
    
    # We should get schema message out, plus the LOG message at the end
    assert len(result_msgs) == 2
    out_schema = result_msgs[0]
    assert out_schema.type == MessageType.SCHEMA
    assert out_schema.schema_info.schema_data["properties"]["age"]["type"] == "integer"
    assert out_schema.schema_info.schema_data["properties"]["name"]["type"] == "string"

    # 2. Test Record Transformation (Valid)
    record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={
                "age": "25",
                "score": "99.9",
                "is_active": "true",
                "date_str": "2023-01-01T12:00:00",
                "name": "rudran"
            }
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([record_msg])))
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert out_record.record.data["age"] == 25
    assert out_record.record.data["score"] == 99.9
    assert out_record.record.data["is_active"] is True
    assert out_record.record.data["date_str"] == "2023-01-01"

    # 3. Test Record Transformation (Invalid safe fail)
    invalid_record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"age": "not-an-int"}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([invalid_record_msg])))
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert out_record.record.data["age"] is None
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=1, passed=1, failed_safe=1" in log_msg.log.message

    # 4. Test Record Transformation (Invalid hard fail)
    config_fail = config.copy()
    config_fail["on_error"] = "fail"
    from flowcore.engine.exceptions.plugin import RecoverablePluginError
    with pytest.raises(RecoverablePluginError):
        list(plugin.transform(config_fail, None, iter([invalid_record_msg])))
