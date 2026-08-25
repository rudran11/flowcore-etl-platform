import pyarrow as pa
import duckdb
from typing import Dict, Any, Iterator
from flowcore_shared.plugins.cdk.batch import MultiInputTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities

class JoinPlugin(MultiInputTransformPlugin):
    """
    Stateful join plugin using DuckDB.
    Supports INNER and LEFT joins across two upstream pipelines.
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-join",
            name="Join",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Joins records from two upstreams.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"]
        )

    def check(self, config: Dict[str, Any]) -> bool:
        return all(k in config for k in ["left_input", "right_input", "join_type", "condition"])

    def transform_multi(self, config: Dict[str, Any], catalog: Any, message_streams: Dict[str, Iterator[FlowCoreMessage]], context: Any) -> Iterator[FlowCoreMessage]:
        left_input_id = config.get("left_input")
        right_input_id = config.get("right_input")
        join_type = config.get("join_type", "INNER").upper()
        condition = config.get("condition")
        
        if left_input_id not in message_streams or right_input_id not in message_streams:
            from flowcore.engine.exceptions.plugin import FatalPluginError
            raise FatalPluginError(f"Missing upstream dependencies for join: required {left_input_id} and {right_input_id}")
            
        left_stream = message_streams[left_input_id]
        right_stream = message_streams[right_input_id]
        
        left_records = []
        right_records = []
        left_schema = {}
        right_schema = {}
        stream_name = "default"
        
        # 1. Consume Streams
        # In a real environment, ThreadPoolExecutor executes these concurrently upstream.
        # Since this node runs in a single thread, consuming from the blocking queues sequentially
        # could cause deadlocks if the upstream threads block on full queues. 
        # But since we use simple iterators in memory, we can just consume them sequentially here.
        # Alternatively, we could consume round-robin. 
        # For this milestone, sequential consumption from in-memory lists is acceptable.
        
        for msg in left_stream:
            if msg.type == MessageType.SCHEMA and msg.schema_info:
                left_schema = msg.schema_info.schema_data
                stream_name = getattr(msg.schema_info, "stream", stream_name)
            elif msg.type == MessageType.RECORD and msg.record:
                left_records.append(msg.record.data)
                stream_name = getattr(msg.record, "stream", stream_name)
            else:
                yield msg
                
        for msg in right_stream:
            if msg.type == MessageType.SCHEMA and msg.schema_info:
                right_schema = msg.schema_info.schema_data
            elif msg.type == MessageType.RECORD and msg.record:
                right_records.append(msg.record.data)
            else:
                yield msg
                
        if not left_records and not right_records:
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message="metrics: matched_records=0"))
            return

        # 2. Setup DuckDB Query
        try:
            con = duckdb.connect(database=':memory:')
            
            # Handle empty datasets
            if left_records:
                left_table = pa.Table.from_pylist(left_records)
                con.register('left_table', left_table)
            else:
                con.execute("CREATE TABLE left_table (dummy INTEGER)")
                
            if right_records:
                right_table = pa.Table.from_pylist(right_records)
                con.register('right_table', right_table)
            else:
                con.execute("CREATE TABLE right_table (dummy INTEGER)")
                
            # If one is empty and it's an INNER join, fast fail
            if join_type == "INNER" and (not left_records or not right_records):
                yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message="metrics: matched_records=0"))
                return
                
            # To avoid ambiguous columns in SELECT *, explicitly alias
            # We'll just use SELECT left_table.*, right_table.* for now, duckdb handles conflicts
            # Wait, duckdb will throw "duplicate column name" if there's a conflict in SELECT *.
            # We must explicitly alias or specify.
            
            left_cols = list(left_schema.keys()) if left_schema else (list(left_records[0].keys()) if left_records else [])
            right_cols = list(right_schema.keys()) if right_schema else (list(right_records[0].keys()) if right_records else [])
            
            select_clauses = []
            for c in left_cols:
                select_clauses.append(f'left_table."{c}" AS "{c}"')
            for c in right_cols:
                if c in left_cols:
                    select_clauses.append(f'right_table."{c}" AS "{c}_right"')
                else:
                    select_clauses.append(f'right_table."{c}" AS "{c}"')
                    
            select_str = ", ".join(select_clauses)
            
            query = f"""
            SELECT {select_str} 
            FROM left_table 
            {join_type} JOIN right_table ON {condition}
            """
                
            result_arrow = con.execute(query).arrow().read_all()
            result_dicts = result_arrow.to_pylist()
            
            # 3. Yield Schema
            new_schema = {}
            for c, t in left_schema.items():
                new_schema[c] = t
            for c, t in right_schema.items():
                if c in left_schema:
                    new_schema[f"{c}_right"] = t
                else:
                    new_schema[c] = t
                    
            yield FlowCoreMessage(
                type=MessageType.SCHEMA,
                schema_info=SchemaMessage(stream=stream_name, schema_data=new_schema)
            )
            
            # 4. Yield Records
            matched_records = 0
            for row in result_dicts:
                yield FlowCoreMessage(
                    type=MessageType.RECORD,
                    record=RecordMessage(stream=stream_name, data=row)
                )
                matched_records += 1
                
            # 5. Yield Metrics
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: left_records={len(left_records)}"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: right_records={len(right_records)}"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: matched_records={matched_records}"))
            
        except Exception as e:
            from flowcore.engine.exceptions.plugin import RecoverablePluginError
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="ERROR", message=f"Join failed: {str(e)}"))
            raise RecoverablePluginError(f"Join error: {str(e)}")
