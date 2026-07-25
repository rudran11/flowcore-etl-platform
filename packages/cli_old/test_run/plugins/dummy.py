
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore_engine.executor.models import ExecutionResult
import time

class DummyPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="dummy",
            name="Dummy Plugin",
            version="1.0.0",
            description="Dummy",
            author="test",
            plugin_type=PluginType.CONNECTOR
        )
        
    def execute(self, runtime_context):
        time.sleep(1.0)
        return {"status": "ok"}
