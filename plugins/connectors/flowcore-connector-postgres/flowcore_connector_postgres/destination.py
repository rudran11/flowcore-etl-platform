# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Any, Dict, Iterator
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.db import retry_on_transient
from pydantic import BaseModel, Field, SecretStr
from typing import Optional

class PostgresConfig(BaseModel):
    host: str = Field("localhost", description="PostgreSQL server hostname or IP address.")
    port: int = Field(5432, description="PostgreSQL server port.")
    database: str = Field("test_db", description="Name of the database to connect to.")
    username: str = Field("postgres", description="Username for authentication.")
    password: Optional[SecretStr] = Field(None, description="Password for authentication.")

class PostgresDestinationPlugin(DestinationPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-postgres",
            name="PostgreSQL Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Loads data into PostgreSQL databases.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=True
            ),
            config_schema=PostgresConfig.model_json_schema()
        )
        
    def _get_conn(self, config: Dict[str, Any]):
        return psycopg2.connect(
            host=config.get("host", "localhost"),
            port=config.get("port", 5432),
            user=config.get("username", "postgres"),
            password=config.get("password", ""),
            dbname=config.get("database", "test_db")
        )

    @retry_on_transient((OperationalError,))
    def check(self, config: Dict[str, Any]) -> bool:
        required = []
        for req in required:
            if not config.get(req):
                raise ValueError(f"Missing '{req}' in config")
        
        with self._get_conn(config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return True
        
    def write(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
        batch_size = config.get("batch_size", 1000)
        buffers = {}
        
        # We will use a single connection with transaction block
        with self._get_conn(config) as conn:
            with conn.cursor() as cur:
                try:
                    for msg in message_stream:
                        if msg.type == MessageType.RECORD and msg.record:
                            stream_name = msg.record.stream
                            data = msg.record.data
                            
                            if stream_name not in buffers:
                                buffers[stream_name] = []
                                
                            buffers[stream_name].append(data)
                            
                            if len(buffers[stream_name]) >= batch_size:
                                self._flush_buffer(stream_name, buffers, cur)
                                
                        elif msg.type == MessageType.STATE:
                            # Flush all buffers before emitting state
                            for stream_name in list(buffers.keys()):
                                if buffers[stream_name]:
                                    self._flush_buffer(stream_name, buffers, cur)
                            # Commit transaction up to this state
                            conn.commit()
                            yield msg
                            
                    # Flush remaining
                    for stream_name in list(buffers.keys()):
                        if buffers[stream_name]:
                            self._flush_buffer(stream_name, buffers, cur)
                    conn.commit()
                    
                except Exception as e:
                    conn.rollback()
                    raise e
                    
    def _flush_buffer(self, stream_name: str, buffers: Dict, cur):
        records = buffers[stream_name]
        if not records:
            return
            
        columns = list(records[0].keys())
        # Use simple string formatting since these are table/column names, 
        # but in production, psycopg2.sql is needed to prevent injection.
        cols_str = ", ".join([f'"{c}"' for c in columns])
        
        # Build the values template
        template = "(" + ", ".join(["%s"] * len(columns)) + ")"
        
        query = f'INSERT INTO "{stream_name}" ({cols_str}) VALUES %s ON CONFLICT DO NOTHING'
        
        # Extract tuple list for execute_values
        data_tuples = [tuple(r.get(c) for c in columns) for r in records]
        
        psycopg2.extras.execute_values(cur, query, data_tuples, template=template, page_size=len(data_tuples))
        buffers[stream_name].clear()
