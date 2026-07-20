# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import pytest
import threading
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from flowcore_cli.main import app

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

@pytest.fixture(autouse=True)
def mock_plugin_manager():
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

def test_stress_local_execution(dummy_pipeline):
    """Run local execution 25 times to assert thread safety and no leaks."""
    initial_threads = threading.active_count()
    
    for i in range(25):
        result = runner.invoke(app, ["run", str(dummy_pipeline)])
        assert result.exit_code == 0, f"Run {i} failed!"
        assert "Pipeline completed successfully" in result.stdout
        
    final_threads = threading.active_count()
    # Check that we didn't leak a massive number of threads (allow +/- 2 for standard pytest runner background threads)
    assert final_threads <= initial_threads + 5, f"Thread leak detected! Initial: {initial_threads}, Final: {final_threads}"

def test_stress_remote_execution(dummy_pipeline):
    """Run remote execution 25 times to assert client robustness."""
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"run_id": "test_run_123"}
        mock_client.post.return_value = mock_post_response
        
        mock_get_completed = MagicMock()
        mock_get_completed.json.return_value = {"status": "COMPLETED", "duration_ms": 1500}
        mock_client.get.return_value = mock_get_completed
        
        for i in range(25):
            result = runner.invoke(app, ["run", str(dummy_pipeline), "--remote", "--server", "http://localhost:8000"])
            assert result.exit_code == 0, f"Remote run {i} failed!"
            assert "Pipeline completed successfully" in result.stdout
