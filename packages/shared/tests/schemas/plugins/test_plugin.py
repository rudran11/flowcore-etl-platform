import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.plugins.plugin import Plugin, PluginType

def test_plugin_creation():
    plugin = Plugin(
        id="postgres-v1",
        name="PostgreSQL Connector",
        plugin_type=PluginType.SOURCE,
        version="1.0.0",
        entrypoint="flowcore_plugins.postgres"
    )
    assert plugin.id == "postgres-v1"
    assert plugin.plugin_type == "SOURCE"
    assert plugin.entrypoint == "flowcore_plugins.postgres"

def test_plugin_invalid_type():
    with pytest.raises(ValidationError):
        Plugin(
            id="postgres-v1",
            name="PostgreSQL Connector",
            plugin_type="INVALID_TYPE",
            version="1.0.0",
            entrypoint="flowcore_plugins.postgres"
        )
