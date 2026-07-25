# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import pytest
from typer.testing import CliRunner
from flowcore_cli.main import app
import os
from unittest.mock import patch, MagicMock

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
    with patch("flowcore_cli.commands.run.PluginManager") as mock_pm_cls, \
         patch("flowcore_engine.plugins.manager.PluginManager") as mock_validate_pm_cls:
        
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
        mock_validate_pm_cls.return_value = mock_instance
        yield

def test_snapshot_doctor():
    result = runner.invoke(app, ["doctor"])
    # Not asserting exit code since tests/ isn't a project, but we can verify the Rich layout
    stdout = result.stdout
    
    assert "FlowCore Doctor" in stdout
    assert "Python Version" in stdout
    assert "Project Config" in stdout
    
def test_snapshot_validate_dry_run(dummy_pipeline, mock_plugin_manager_success):
    result = runner.invoke(app, ["validate", str(dummy_pipeline), "--dry-run"])
    stdout = result.stdout
    
    assert result.exit_code == 0
    assert "Validating" in stdout
    assert "Execution Plan" in stdout
    assert "Validation Summary" in stdout
    assert "Ready to Execute" in stdout
    assert "s1" in stdout

def test_snapshot_local_run(dummy_pipeline):
    with patch("flowcore_cli.commands.run.PluginManager") as mock_pm_cls:
        mock_instance = MagicMock()
        mock_instance._instance_registry = {"dummy": True}
        def fake_get_plugin(pid):
            plugin = MagicMock()
            res = MagicMock()
            res.success = True
            plugin.execute.return_value = res
            return plugin
        mock_instance.get_plugin = fake_get_plugin
        mock_pm_cls.return_value = mock_instance
        
        result = runner.invoke(app, ["run", str(dummy_pipeline)])
        stdout = result.stdout
        
        assert result.exit_code == 0
        # Check standard Rich panel/CLI layout output
        assert "Running Pipeline" in stdout
        assert "Pipeline completed successfully" in stdout
        assert "Steps:" in stdout
        assert "Duration:" in stdout
        assert "Failures:   0" in stdout
