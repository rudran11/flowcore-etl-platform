import pytest
from unittest.mock import MagicMock
from flowcore.engine.plugins.manager import PluginManager
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore_server.main import app
from flowcore_server.dependencies.engine import get_plugin_manager

@pytest.fixture
def mock_plugin_manager():
    manager = MagicMock(spec=PluginManager)
    
    # Mock plugins
    plugin1 = MagicMock()
    plugin1.metadata = PluginMetadata(
        plugin_id="plugin-1",
        name="Plugin One",
        version="1.0.0",
        plugin_type=PluginType.CONNECTOR,
        author="Author",
        description="A plugin"
    )
    
    plugin2 = MagicMock()
    plugin2.metadata = PluginMetadata(
        plugin_id="plugin-2",
        name="Plugin Two",
        version="2.0.0",
        plugin_type=PluginType.TRANSFORMER,
        author="Author 2",
        description="Another plugin"
    )
    
    manager.list_plugins.return_value = [plugin1.metadata, plugin2.metadata]
    
    def get_plugin_side_effect(plugin_id):
        if plugin_id == "plugin-1":
            return plugin1
        elif plugin_id == "plugin-2":
            return plugin2
        from flowcore.engine.exceptions.plugin import PluginLoadError
        raise PluginLoadError(plugin_id, "Not found")
        
    manager.get_plugin.side_effect = get_plugin_side_effect
    return manager

@pytest.fixture
def client_with_mock(client, mock_plugin_manager):
    app.dependency_overrides[get_plugin_manager] = lambda: mock_plugin_manager
    yield client
    app.dependency_overrides.clear()

def test_list_plugins(client_with_mock):
    response = client_with_mock.get("/api/v1/plugins")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["plugin_id"] == "plugin-1"
    assert data[1]["plugin_id"] == "plugin-2"

def test_get_plugin_success(client_with_mock):
    response = client_with_mock.get("/api/v1/plugins/plugin-1")
    assert response.status_code == 200
    data = response.json()
    assert data["plugin_id"] == "plugin-1"
    assert data["name"] == "Plugin One"

def test_get_plugin_not_found(client_with_mock):
    response = client_with_mock.get("/api/v1/plugins/plugin-not-found")
    assert response.status_code == 500
    data = response.json()
    assert data["flowcore_code"] == "FLOWCORE-1001"
