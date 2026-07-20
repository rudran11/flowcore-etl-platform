import pytest
from flowcore_shared.exceptions import FlowCoreError, MetadataError, ValidationError, PluginError

def test_flowcore_error_inheritance():
    err = FlowCoreError("Base error")
    assert isinstance(err, Exception)
    assert err.message == "Base error"

def test_metadata_error():
    err = MetadataError("Meta error")
    assert isinstance(err, FlowCoreError)

def test_validation_error():
    err = ValidationError("Validation failed")
    assert isinstance(err, FlowCoreError)

def test_plugin_error():
    err = PluginError("Plugin crashed")
    assert isinstance(err, FlowCoreError)
