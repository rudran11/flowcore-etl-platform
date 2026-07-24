from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType

class SlackPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="flowcore-slack",
            name="Slack Notifications",
            version="2.0.1",
            plugin_type=PluginType.ACTION,
            author="FlowCore Notifications",
            description="Send messages and alerts to Slack channels.",
            category="Notifications",
            capabilities=["SendMessage", "UploadFile"],
            supported_operations=["send_message"],
            example_yaml="type: slack\nchannel: #alerts\nmessage: 'Pipeline {{ pipeline.id }} failed.'",
            documentation="## Slack Plugin\nRequires a Slack Bot Token.",
            compatibility=">=1.0.0",
            dependencies=[]
        )
        
    def execute(self, *args, **kwargs):
        pass
