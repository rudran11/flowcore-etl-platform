from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType

class SlackPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="flowcore-slack",
            name="Slack Notifications",
            version="2.0.1",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Notifications",
            description="Send messages and alerts to Slack channels.",
            category="Notifications",
            capabilities=ConnectorCapabilities(),
            supported_operations=["send_message"],
            example_yaml="type: slack\nchannel: #alerts\nmessage: 'Pipeline {{ pipeline.id }} failed.'",
            documentation="## Slack Plugin\nRequires a Slack Bot Token.",
            flowcore_version_constraint=">=1.0.0",
            dependencies=[]
        )
        
    def execute(self, context, *args, **kwargs):
        # Mock dataset reporting for Lineage testing
        context.report_input_dataset(name="sales_extracted", dataset_type="FILE")
        context.report_output_dataset(name="slack_alerts", dataset_type="API")
        
        class MockResult:
            def __init__(self):
                self.output = {"status": "success", "message": "Sent to Slack"}
        
        return MockResult()
