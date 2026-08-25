import pyarrow as pa
import duckdb
from typing import Dict, Any, Iterator
from flowcore_shared.plugins.cdk.batch import BatchTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities

class SortPlugin(BatchTransformPlugin):
    """
    Stateful sort plugin using DuckDB.
    Supports single or multiple columns with ASC/DESC and null handling.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-sort",
            name="Sort",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Sorts records.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"]
        )

    def check(self, config: Dict[str, Any]) -> bool:
        return "sort_by" in config

    def transform_batch(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage], context: Any) -> Iterator[FlowCoreMessage]:
        sort_by = config.get("sort_by", [])
        
        records = []
        schema_data = {}
        stream_name = "default"
        
        # 1. Consume Stream
        records_received = 0
        for msg in message_stream:
            if msg.type == MessageType.SCHEMA and msg.schema_info:
                schema_data = msg.schema_info.schema_data
                stream_name = getattr(msg.schema_info, "stream", stream_name)
            elif msg.type == MessageType.RECORD and msg.record:
                records.append(msg.record.data)
                stream_name = getattr(msg.record, "stream", stream_name)
                records_received += 1
            else:
                yield msg
                
        if not records:
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_received=0"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_sorted=0"))
            return

        # 2. Setup DuckDB Query
        try:
            arrow_table = pa.Table.from_pylist(records)
            con = duckdb.connect(database=':memory:')
            con.register('input_table', arrow_table)
            
            order_clauses = []
            for s in sort_by:
                col = s.get("column")
                direction = s.get("direction", "ASC").upper()
                nulls = s.get("nulls", "LAST").upper()
                order_clauses.append(f'"{col}" {direction} NULLS {nulls}')
                
            order_str = ", ".join(order_clauses)
            query = f"SELECT * FROM input_table ORDER BY {order_str}"
                
            result_arrow = con.execute(query).arrow().read_all()
            result_dicts = result_arrow.to_pylist()
            
            # 3. Yield Schema
            yield FlowCoreMessage(
                type=MessageType.SCHEMA,
                schema_info=SchemaMessage(stream=stream_name, schema_data=schema_data)
            )
            
            # 4. Yield Records
            records_sorted = 0
            for row in result_dicts:
                yield FlowCoreMessage(
                    type=MessageType.RECORD,
                    record=RecordMessage(stream=stream_name, data=row)
                )
                records_sorted += 1
                
            # 5. Yield Metrics
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_received={records_received}"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_sorted={records_sorted}"))
            
        except Exception as e:
            from flowcore.engine.exceptions.plugin import RecoverablePluginError
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="ERROR", message=f"Sort failed: {str(e)}"))
            raise RecoverablePluginError(f"Sort error: {str(e)}")
