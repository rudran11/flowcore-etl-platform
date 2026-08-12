# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Any, Dict, Iterator
import pymysql

from flowcore_shared.plugins.cdk.destination import DestinationPlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.db import retry_on_transient
from pydantic import BaseModel, Field, SecretStr
from typing import Optional

class MysqlConfig(BaseModel):
    host: str = Field(..., description="MySQL server hostname or IP address.", json_schema_extra={"placeholder": "localhost"})
    port: int = Field(3306, description="MySQL server port.")
    database: str = Field(..., description="Name of the database to connect to.", json_schema_extra={"placeholder": "my_db"})
    username: str = Field(..., description="Username for authentication.")
    password: Optional[SecretStr] = Field(None, description="Password for authentication.")

class MysqlDestinationPlugin(DestinationPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="destination-mysql",
            name="MySQL Destination",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Loads data into MySQL databases.",
            connector_type="Destination",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=False,
                supports_schema_discovery=False,
                supports_parallel_read=False,
                supports_batch_write=True
            ),
            config_schema=MysqlConfig.model_json_schema()
        )
        
    def _get_conn(self, config: Dict[str, Any]):
        return pymysql.connect(
            host=config.get("host", "localhost"),
            port=config.get("port", 3306),
            user=config.get("username", "root"),
            password=config.get("password", ""),
            database=config.get("database", "test_db")
        )

    @retry_on_transient((pymysql.OperationalError,))
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
                            for stream_name in list(buffers.keys()):
                                if buffers[stream_name]:
                                    self._flush_buffer(stream_name, buffers, cur)
                            conn.commit()
                            yield msg
                            
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
        cols_str = ", ".join([f"`{c}`" for c in columns])
        
        # Build the values template
        template = ", ".join(["%s"] * len(columns))
        
        # INSERT IGNORE is used in MySQL for "ON CONFLICT DO NOTHING"
        query = f"INSERT IGNORE INTO `{stream_name}` ({cols_str}) VALUES ({template})"
        
        data_tuples = [tuple(r.get(c) for c in columns) for r in records]
        
        cur.executemany(query, data_tuples)
        buffers[stream_name].clear()
