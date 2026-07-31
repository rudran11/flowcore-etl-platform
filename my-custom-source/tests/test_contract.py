import pytest
from my_custom_source.plugin import MyCustomSourcePlugin

def test_plugin_metadata():
    plugin = MyCustomSourcePlugin()
    assert plugin.metadata.name == "my-custom-source"
    assert plugin.metadata.connector_type == "Source"

def test_plugin_check():
    plugin = MyCustomSourcePlugin()
    assert plugin.check({"api_key": "test"} if "source" == "source" else {})
