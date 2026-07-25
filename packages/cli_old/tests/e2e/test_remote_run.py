# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from flowcore_cli.main import app
import httpx
import os
from flowcore_cli.client.api import FlowCoreClientError

runner = CliRunner()

@pytest.fixture
def mock_httpx_success():
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        # Mock POST /execute
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"run_id": "test_run_123"}
        mock_client.post.return_value = mock_post_response
        
        # Mock GET /status (first RUNNING, then COMPLETED)
        mock_get_running = MagicMock()
        mock_get_running.json.return_value = {"status": "RUNNING", "duration_ms": 100}
        
        mock_get_completed = MagicMock()
        mock_get_completed.json.return_value = {"status": "COMPLETED", "duration_ms": 1500}
        
        mock_client.get.side_effect = [mock_get_running, mock_get_completed]
        
        yield mock_client

@pytest.fixture(autouse=True)
def mock_plugin_manager():
    with patch("flowcore_cli.commands.run.PluginManager") as mock_pm_cls:
        mock_instance = MagicMock()
        mock_instance._instance_registry = {"dummy": True}
        mock_pm_cls.return_value = mock_instance
        yield

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

def test_remote_execution_success(mock_httpx_success, dummy_pipeline):
    result = runner.invoke(app, ["run", str(dummy_pipeline), "--remote", "--server", "http://localhost:8000"])
    assert result.exit_code == 0
    assert "Submitting pipeline to server at http://localhost:8000..." in result.stdout
    assert "Run ID: test_run_123" in result.stdout
    assert "[✓] Pipeline Execution (Status: COMPLETED)" in result.stdout
    assert "Pipeline completed successfully" in result.stdout

def test_remote_execution_missing_server(dummy_pipeline):
    result = runner.invoke(app, ["run", str(dummy_pipeline), "--remote"])
    # No --server flag and no flowcore.toml
    assert result.exit_code == 2
    assert "Server URL must be provided" in result.stdout

def test_remote_execution_failure(dummy_pipeline):
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"run_id": "test_run_fail"}
        mock_client.post.return_value = mock_post_response
        
        mock_get_failed = MagicMock()
        mock_get_failed.json.return_value = {"status": "FAILED", "duration_ms": 1500, "error": "Plugin failed"}
        mock_client.get.return_value = mock_get_failed
        
        result = runner.invoke(app, ["run", str(dummy_pipeline), "--remote", "--server", "http://localhost:8000"])
        
        assert result.exit_code == 1
        assert "Pipeline failed" in result.stdout
        assert "Error: Plugin failed" in result.stdout

def test_remote_execution_connection_error(dummy_pipeline):
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_client.post.side_effect = httpx.RequestError("Connection refused")
        
        result = runner.invoke(app, ["run", str(dummy_pipeline), "--remote", "--server", "http://localhost:8000"])
        
        assert result.exit_code == 3
        assert "Unable to connect to FlowCore Server" in result.stdout
        assert "Connection error: Connection refused" in result.stdout
