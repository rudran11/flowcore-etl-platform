from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
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
        time.sleep(0.1)
        return {"status": "ok"}
