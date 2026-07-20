# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from flowcore_cli.main import app
import os

runner = CliRunner()

@pytest.fixture
def dummy_pipeline(tmp_path):
    pipe_file = tmp_path / "pipeline.yaml"
    pipe_file.write_text("""
version: '1.0'
pipeline:
  name: test_pipe
  owner: test
steps:
  - step_id: s1
    connector_id: dummy
""")
    return pipe_file

@pytest.fixture
def mock_plugin_manager_success():
    with patch("flowcore_cli.commands.run.PluginManager") as mock_pm_cls:
        mock_instance = MagicMock()
        mock_instance._instance_registry = {"dummy": True}
        def fake_get_plugin(pid):
            plugin = MagicMock()
            result = MagicMock()
            result.success = True
            result.data = {"status": "ok"}
            plugin.execute.return_value = result
            return plugin
        mock_instance.get_plugin = fake_get_plugin
        mock_pm_cls.return_value = mock_instance
        yield

def test_local_execution_success(dummy_pipeline, mock_plugin_manager_success):
    result = runner.invoke(app, ["run", str(dummy_pipeline)])
    assert result.exit_code == 0
    assert "Running Pipeline" in result.stdout
    assert "Pipeline completed successfully" in result.stdout

def test_local_execution_failure(dummy_pipeline):
    from flowcore_engine.exceptions.plugin import FatalPluginError

    # Mock a failure
    with patch("flowcore_cli.commands.run.PluginManager") as mock_pm_cls:
        mock_instance = MagicMock()
        mock_instance._instance_registry = {"dummy": True}
        def fake_get_plugin(pid):
            plugin = MagicMock()
            plugin.execute.side_effect = FatalPluginError("Simulated plugin crash")
            return plugin
        mock_instance.get_plugin = fake_get_plugin
        mock_pm_cls.return_value = mock_instance
        
        result = runner.invoke(app, ["run", str(dummy_pipeline)])
        if result.exit_code != 1:
            raise AssertionError(f"Expected exit code 1, got {result.exit_code}. Output: {repr(result.stdout)}")
