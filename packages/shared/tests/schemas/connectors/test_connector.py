import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.connectors.connector import Connector
from flowcore_shared.schemas.connectors.secret_reference import SecretReference

def test_connector_creation():
    connector = Connector(
        id="prod-db",
        plugin_id="postgres-v1",
        name="Production Database",
        parameters={
            "host": "localhost",
            "port": 5432,
            "password": SecretReference(env_var="PROD_DB_PASSWORD")
        }
    )
    assert connector.id == "prod-db"
    assert connector.plugin_id == "postgres-v1"
    assert "password" in connector.parameters
    assert isinstance(connector.parameters["password"], SecretReference)
