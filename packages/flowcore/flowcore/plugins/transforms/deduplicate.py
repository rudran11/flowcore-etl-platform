import pyarrow as pa
import duckdb
from typing import Dict, Any, Iterator
from flowcore_shared.plugins.cdk.batch import BatchTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities

class DeduplicatePlugin(BatchTransformPlugin):
    """
    Stateful deduplication plugin using DuckDB.
    Supports single or multiple keys, keeping first or last.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-deduplicate",
            name="Deduplicate",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Removes duplicate records.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"]
        )

    def check(self, config: Dict[str, Any]) -> bool:
        return "keys" in config

    def transform_batch(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage], context: Any) -> Iterator[FlowCoreMessage]:
        keys = config.get("keys", [])
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split(",") if k.strip()]
            
        keep = config.get("keep", "first").lower()
        
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
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_emitted=0"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: duplicates_removed=0"))
            return

        # 2. Setup DuckDB Query
        try:
            # Add synthetic sequence for deterministic keep first/last
            for i, r in enumerate(records):
                r["__seq"] = i
                
            arrow_table = pa.Table.from_pylist(records)
            con = duckdb.connect(database=':memory:')
            con.register('input_table', arrow_table)
            
            partition_str = ", ".join([f'"{k}"' for k in keys])
            
            if keep == "first":
                order_clause = "ORDER BY __seq ASC"
            elif keep == "last":
                order_clause = "ORDER BY __seq DESC"
            else:
                order_clause = "ORDER BY __seq ASC"
                
            query = f"""
            SELECT * EXCLUDE (_rn, __seq) FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY {partition_str} {order_clause}) as _rn 
                FROM input_table
            ) WHERE _rn = 1
            """
                
            result_arrow = con.execute(query).arrow().read_all()
            result_dicts = result_arrow.to_pylist()
            
            # 3. Yield Schema
            yield FlowCoreMessage(
                type=MessageType.SCHEMA,
                schema_info=SchemaMessage(stream=stream_name, schema_data=schema_data)
            )
            
            # 4. Yield Records
            records_emitted = 0
            for row in result_dicts:
                yield FlowCoreMessage(
                    type=MessageType.RECORD,
                    record=RecordMessage(stream=stream_name, data=row)
                )
                records_emitted += 1
                
            # 5. Yield Metrics
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_received={records_received}"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_emitted={records_emitted}"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: duplicates_removed={records_received - records_emitted}"))
            
        except Exception as e:
            from flowcore.engine.exceptions.plugin import RecoverablePluginError
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="ERROR", message=f"Deduplicate failed: {str(e)}"))
            raise RecoverablePluginError(f"Deduplicate error: {str(e)}")
