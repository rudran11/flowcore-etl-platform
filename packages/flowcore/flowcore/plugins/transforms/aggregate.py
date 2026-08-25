import pyarrow as pa
import duckdb
from typing import Dict, Any, Iterator
from flowcore_shared.plugins.cdk.batch import BatchTransformPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, SchemaMessage, LogMessage

from flowcore_shared.plugins.models import PluginMetadata, PluginType, ConnectorCapabilities

class AggregatePlugin(BatchTransformPlugin):
    """
    Stateful aggregation plugin using DuckDB.
    Supports GROUP BY and metrics (COUNT, SUM, AVG, MIN, MAX).
    """
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="transform-aggregate",
            name="Aggregate",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="FlowCore",
            description="Aggregates records using group by.",
            category="Transform",
            connector_type="Transform",
            capabilities=ConnectorCapabilities(),
            supported_operations=["transform"]
        )

    def check(self, config: Dict[str, Any]) -> bool:
        return "aggregations" in config

    def transform_batch(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage], context: Any) -> Iterator[FlowCoreMessage]:
        group_by = config.get("group_by", [])
        if isinstance(group_by, str):
            group_by = [g.strip() for g in group_by.split(",") if g.strip()]
            
        aggregations = config.get("aggregations", [])
        
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
                yield msg # Pass through logs
                
        if not records:
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_received=0"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: groups_created=0"))
            return

        # 2. Setup DuckDB Query
        try:
            arrow_table = pa.Table.from_pylist(records)
            con = duckdb.connect(database=':memory:')
            con.register('input_table', arrow_table)
            
            select_clauses = []
            for gb in group_by:
                select_clauses.append(f'"{gb}"')
                
            for agg in aggregations:
                col = agg.get("column")
                func = agg.get("function", "count").upper()
                alias = agg.get("alias", f"{func.lower()}_{col}")
                
                if func not in ["SUM", "COUNT", "AVG", "MIN", "MAX"]:
                    raise ValueError(f"Invalid aggregation function: {func}")
                
                if func in ["SUM", "AVG", "MIN", "MAX"]:
                    select_clauses.append(f'{func}(CAST("{col}" AS DOUBLE)) AS "{alias}"')
                else:
                    select_clauses.append(f'{func}("{col}") AS "{alias}"')
                
            select_str = ", ".join(select_clauses)
            
            if group_by:
                group_str = "GROUP BY " + ", ".join([f'"{gb}"' for gb in group_by])
                query = f"SELECT {select_str} FROM input_table {group_str}"
            else:
                query = f"SELECT {select_str} FROM input_table"
                
            result_arrow = con.execute(query).arrow().read_all()
            result_dicts = result_arrow.to_pylist()
            
            # 3. Yield New Schema
            new_schema = {}
            for gb in group_by:
                if gb in schema_data:
                    new_schema[gb] = schema_data[gb]
            
            for agg in aggregations:
                func = agg.get("function", "count").upper()
                alias = agg.get("alias", f"{func.lower()}_{agg.get('column')}")
                if func == "COUNT":
                    new_schema[alias] = "integer"
                else:
                    new_schema[alias] = "number" # Approximate for float/double
                    
            yield FlowCoreMessage(
                type=MessageType.SCHEMA,
                schema_info=SchemaMessage(stream=stream_name, schema_data=new_schema)
            )
            
            # 4. Yield Records
            groups_created = 0
            for row in result_dicts:
                yield FlowCoreMessage(
                    type=MessageType.RECORD,
                    record=RecordMessage(stream=stream_name, data=row)
                )
                groups_created += 1
                
            # 5. Yield Metrics
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: records_received={records_received}"))
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="INFO", message=f"metrics: groups_created={groups_created}"))
            
        except Exception as e:
            from flowcore.engine.exceptions.plugin import RecoverablePluginError
            yield FlowCoreMessage(type=MessageType.LOG, log=LogMessage(level="ERROR", message=f"Aggregate failed: {str(e)}"))
            raise RecoverablePluginError(f"Aggregate error: {str(e)}")
