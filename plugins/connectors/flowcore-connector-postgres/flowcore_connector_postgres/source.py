# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Any, Dict, Iterator, List, Optional
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.db import retry_on_transient
from flowcore_shared.plugins.framework.schema import infer_schema

class PostgresSourcePlugin(SourcePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-postgres",
            name="PostgreSQL Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts data from PostgreSQL databases.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=True,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            )
        )
        
    def _get_conn(self, config: Dict[str, Any]):
        return psycopg2.connect(
            host=config["host"],
            port=config.get("port", 5432),
            user=config["username"],
            password=config["password"],
            dbname=config["database"]
        )

    @retry_on_transient((OperationalError,))
    def check(self, config: Dict[str, Any]) -> bool:
        required = ["host", "username", "password", "database"]
        for req in required:
            if not config.get(req):
                raise ValueError(f"Missing '{req}' in config")
        
        with self._get_conn(config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return True
        
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        streams = []
        with self._get_conn(config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [r[0] for r in cur.fetchall()]
                
                for table in tables:
                    # Sample 100 rows to infer schema (production uses information_schema.columns)
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
                        dict_cur.execute(f"SELECT * FROM {table} LIMIT 100;")
                        sample = [dict(row) for row in dict_cur.fetchall()]
                        
                        schema = infer_schema(sample)
                        streams.append({"stream": table, "json_schema": schema})
        return streams
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        # Simple read implementation. Usually catalog tells us which streams to read.
        # For this PoC, we will read from the first table in discover, or one specified in config.
        table_name = config.get("table", "users")
        replication_key = config.get("replication_key")
        
        cursor_value = None
        if state and table_name in state:
            cursor_value = state[table_name].get(replication_key)

        with self._get_conn(config) as conn:
            # Server-side cursor for streaming
            with conn.cursor(name="stream_cursor", cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.itersize = 2000
                
                query = f"SELECT * FROM {table_name}"
                params = []
                
                if replication_key and cursor_value:
                    query += f" WHERE {replication_key} > %s ORDER BY {replication_key} ASC"
                    params.append(cursor_value)
                elif replication_key:
                    query += f" ORDER BY {replication_key} ASC"
                    
                cur.execute(query, params)
                
                max_cursor = cursor_value
                
                for row in cur:
                    record = dict(row)
                    yield FlowCoreMessage(
                        type=MessageType.RECORD,
                        record=RecordMessage(stream=table_name, data=record)
                    )
                    
                    if replication_key and record.get(replication_key) is not None:
                        val = record[replication_key]
                        if max_cursor is None or val > max_cursor:
                            max_cursor = val
                            
                # Emit state at the end
                if replication_key and max_cursor is not None:
                    new_state = {table_name: {replication_key: max_cursor}}
                    yield FlowCoreMessage(
                        type=MessageType.STATE,
                        state=StateMessage(state_data=new_state)
                    )
