import pytest
import os
import tempfile
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore.engine.plugins.manager import PluginManager
from flowcore.engine.plugins.enums import PluginLifecycleState
from flowcore.engine.exceptions.plugin import PluginLoadError

# We will create temporary directories and python files to test dynamic loading.

VALID_PLUGIN_CODE = """
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType

class ValidPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="test.valid",
            name="Valid Plugin",
            version="1.0.0",
            plugin_type=PluginType.CONNECTOR,
            author="Test",
            description="A valid test plugin"
        )
        
    def execute(self, context: Any) -> Any:
        return "success"
"""

DUPLICATE_PLUGIN_CODE = """
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType

class DuplicatePlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="test.valid",  # Same ID as ValidPlugin
            name="Duplicate Plugin",
            version="1.0.0",
            plugin_type=PluginType.CONNECTOR,
            author="Test",
            description="A duplicate test plugin"
        )
        
    def execute(self, context: Any) -> Any:
        return "duplicate"
"""

MALFORMED_PLUGIN_CODE = """
# Syntax error ahead
def broken_function(
"""

MISSING_EXECUTE_CODE = """
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType

class MissingExecutePlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="test.missing",
            name="Missing Execute",
            version="1.0.0",
            plugin_type=PluginType.TRANSFORMER,
            author="Test",
            description="Missing execute"
        )
    # No execute method! This will fail ABC instantiation.
"""

def test_valid_plugin_discovery():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "valid.py"), "w") as f:
            f.write(VALID_PLUGIN_CODE)
            
        manager = PluginManager()
        manager.discover_plugins([temp_dir])
        
        plugin = manager.get_plugin("test.valid")
        assert isinstance(plugin, BasePlugin)
        
        metadata = manager.get_metadata("test.valid")
        assert metadata.plugin_id == "test.valid"
        assert metadata.version == "1.0.0"
        
        state = manager.get_lifecycle_state("test.valid")
        assert state == PluginLifecycleState.READY

def test_duplicate_plugin_ids():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "valid.py"), "w") as f:
            f.write(VALID_PLUGIN_CODE)
        with open(os.path.join(temp_dir, "dup.py"), "w") as f:
            f.write(DUPLICATE_PLUGIN_CODE)
            
        manager = PluginManager()
        with pytest.raises(PluginLoadError) as exc:
            manager.discover_plugins([temp_dir])
        assert "Duplicate plugin_id detected" in str(exc.value)

def test_malformed_plugin_import():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "malformed.py"), "w") as f:
            f.write(MALFORMED_PLUGIN_CODE)
            
        manager = PluginManager()
        with pytest.raises(PluginLoadError) as exc:
            manager.discover_plugins([temp_dir])
        assert "Malformed plugin import" in str(exc.value)

def test_missing_execute_method():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "missing.py"), "w") as f:
            f.write(MISSING_EXECUTE_CODE)
            
        manager = PluginManager()
        manager.discover_plugins([temp_dir])
        
        # It is skipped during discovery because it's evaluated as an abstract class
        plugins = manager.list_plugins()
        assert len(plugins) == 0
