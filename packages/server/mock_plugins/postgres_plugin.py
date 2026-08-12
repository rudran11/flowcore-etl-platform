from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field, SecretStr, ValidationError
from typing import Optional

class PostgresConfig(BaseModel):
    host: str = Field(..., description="PostgreSQL server hostname or IP address.", json_schema_extra={"placeholder": "localhost"})
    port: int = Field(5432, description="PostgreSQL server port.")
    database: str = Field(..., description="Name of the database to connect to.", json_schema_extra={"placeholder": "my_db"})
    username: str = Field(..., description="Username for authentication.")
    password: Optional[SecretStr] = Field(None, description="Password for authentication.")
    ssl_mode: str = Field("prefer", description="SSL mode for the connection.", json_schema_extra={"enum": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]})
    query: Optional[str] = Field(None, description="Custom SQL query to extract data. If not provided, a table must be specified.", json_schema_extra={"format": "multiline", "placeholder": "SELECT * FROM users"})

class PostgresPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="flowcore-postgres",
            name="PostgreSQL Connector",
            version="1.2.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Data",
            description="Enterprise connector for PostgreSQL databases.",
            category="Database",
            capabilities=ConnectorCapabilities(supports_incremental=True, supports_schema_discovery=True),
            supported_operations=["query", "insert", "bulk_copy"],
            example_yaml="type: postgres\nhost: localhost\nport: 5432\ndatabase: my_db\nusername: admin\nquery: SELECT * FROM users",
            documentation="## PostgreSQL Plugin\nAllows querying and loading data into Postgres databases.",
            config_schema=PostgresConfig.model_json_schema(),
            flowcore_version_constraint=">=1.0.0",
            dependencies=[]
        )

    def validate_config(self, config: dict) -> dict:
        try:
            PostgresConfig.model_validate(config)
            return {"success": True, "warnings": [], "errors": []}
        except ValidationError as e:
            errors = [f"{err['loc'][0] if err['loc'] else 'config'}: {err['msg']}" for err in e.errors()]
            return {"success": False, "warnings": [], "errors": errors}
        
    def execute(self, context, *args, **kwargs):
        # Mock dataset reporting for Lineage testing
        context.report_input_dataset(name="sales_db", dataset_type="DATABASE_TABLE")
        context.report_output_dataset(name="sales_extracted", dataset_type="FILE")
        
        return {"status": "success", "rows_processed": 100}
