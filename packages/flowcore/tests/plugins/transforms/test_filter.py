import pytest
from flowcore.plugins.transforms.filter import FilterTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

def test_filter_plugin():
    plugin = FilterTransformPlugin()
    config = {
        "conditions": [
            {"field": "status", "operator": "==", "value": "COMPLETED"},
            {"field": "amount", "operator": ">", "value": 50}
        ]
    }

    # 1. Test Schema Mutation (should be pass-through)
    schema_msg = FlowCoreMessage(
        type=MessageType.SCHEMA,
        schema_info=SchemaMessage(
            stream="test_stream",
            schema_data={"properties": {"status": {"type": "string"}, "amount": {"type": "integer"}}}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([schema_msg])))
    assert len(result_msgs) == 2
    out_schema = result_msgs[0]
    assert out_schema.type == MessageType.SCHEMA
    assert out_schema.schema_info.schema_data == schema_msg.schema_info.schema_data

    # 2. Test Record Transformation (Valid)
    valid_record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"status": "COMPLETED", "amount": 100}
        )
    )
    
    invalid_record_msg = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"status": "FAILED", "amount": 100}
        )
    )
    
    invalid_record_msg2 = FlowCoreMessage(
        type=MessageType.RECORD,
        record=RecordMessage(
            stream="test_stream",
            data={"status": "COMPLETED", "amount": 20}
        )
    )

    result_msgs = list(plugin.transform(config, None, iter([valid_record_msg, invalid_record_msg, invalid_record_msg2])))
    
    # Only 1 record should pass, plus 1 log message
    assert len(result_msgs) == 2
    out_record = result_msgs[0]
    assert out_record.type == MessageType.RECORD
    assert out_record.record.data == valid_record_msg.record.data
    
    log_msg = result_msgs[1]
    assert log_msg.type == MessageType.LOG
    assert "received=3, passed=1, filtered=2" in log_msg.log.message
