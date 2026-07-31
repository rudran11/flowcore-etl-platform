import pytest
from test_source_final.plugin import TestSourceFinalPlugin

def test_plugin_metadata():
    plugin = TestSourceFinalPlugin()
    assert plugin.metadata.name == "test-source-final"
    assert plugin.metadata.connector_type == "Source"

def test_plugin_check():
    plugin = TestSourceFinalPlugin()
    assert plugin.check({"api_key": "test"} if "source" == "source" else {})
