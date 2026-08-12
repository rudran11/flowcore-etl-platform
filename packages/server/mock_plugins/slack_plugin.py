from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from pydantic import BaseModel, Field, SecretStr, ValidationError
from typing import Optional

class SlackConfig(BaseModel):
    api_token: SecretStr = Field(..., description="Slack API Token starting with xoxb- or xoxp-.")
    channel: str = Field(..., description="Channel name or ID to post to.", json_schema_extra={"placeholder": "#general"})
    message_format: str = Field("text", description="Format of the message.", json_schema_extra={"enum": ["text", "blocks", "markdown"]})
    bot_name: Optional[str] = Field("FlowCore Bot", description="Display name for the bot.")

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
            example_yaml="type: slack\napi_token: xoxb-123...\nchannel: '#alerts'\nmessage_format: markdown",
            documentation="## Slack Notification Plugin\nSends alert messages to Slack channels.",
            config_schema=SlackConfig.model_json_schema(),
            flowcore_version_constraint=">=1.0.0",
            dependencies=[]
        )

    def validate_config(self, config: dict) -> dict:
        try:
            SlackConfig.model_validate(config)
            return {"success": True, "warnings": [], "errors": []}
        except ValidationError as e:
            errors = [f"{err['loc'][0] if err['loc'] else 'config'}: {err['msg']}" for err in e.errors()]
            return {"success": False, "warnings": [], "errors": errors}
        
    def execute(self, context, *args, **kwargs):
        # Mock dataset reporting for Lineage testing
        context.report_input_dataset(name="sales_extracted", dataset_type="FILE")
        context.report_output_dataset(name="slack_alerts", dataset_type="API")
        
        class MockResult:
            def __init__(self):
                self.output = {"status": "success", "message": "Sent to Slack"}
        
        return MockResult()
