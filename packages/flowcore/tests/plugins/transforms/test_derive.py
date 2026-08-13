import pytest
from flowcore.plugins.transforms.derive import DeriveTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

def test_derive_plugin():
    plugin = DeriveTransformPlugin()
    config = {
        "column": "discounted_price",
        "expression": "price * 0.9",
        "on_error": "null"
    }

    # 1. Test Schema Mutation
    schema_msg = FlowCoreMessage(
        type=MessageType.SCHEMA,
        schema_info=SchemaMessage(
            stream="test_stream",
            schema_data={"properties": {"id": {"type": "string"}, "price": {"type": "integer"}}}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([schema_msg])))
    assert len(result_msgs) == 2
    out_schema = result_msgs[0]
    assert out_schema.type == MessageType.SCHEMA
    assert "discounted_price" in out_schema.schema_info.schema_data["properties"]

    # 2. Test Record Transformation (Valid)
    record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"id": "1", "price": 100}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([record_msg])))
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert out_record.record.data["discounted_price"] == 90.0
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=1, passed=1, failed_safe=0" in log_msg.log.message

    # 3. Test Record Transformation (Invalid safe fail)
    invalid_record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"id": "2", "price": "not-a-number"}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([invalid_record_msg])))
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert out_record.record.data["discounted_price"] is None
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=1, passed=1, failed_safe=1" in log_msg.log.message

    # 4. Test Record Transformation (Invalid hard fail)
    config_fail = config.copy()
    config_fail["on_error"] = "fail"
    from flowcore.engine.exceptions.plugin import RecoverablePluginError
    with pytest.raises(RecoverablePluginError):
        list(plugin.transform(config_fail, None, iter([invalid_record_msg])))
