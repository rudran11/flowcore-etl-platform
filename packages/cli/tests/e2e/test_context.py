# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
from pathlib import Path
from rich.console import Console
from flowcore_cli.context import CLIContext, create_context

def test_cli_context_defaults():
    console = Console()
    ctx = CLIContext(console=console, verbose=False)
    
    assert ctx.verbose is False
    assert ctx.server_url == "http://localhost:8000"
    assert ctx.execution_mode == "local"

def test_cli_context_load_config(tmp_path):
    # Create a dummy flowcore.toml in tmp_path
    config_content = """
[project]
name = "test-project"

[server]
url = "http://remote-server:9000"

[execution]
mode = "remote"
    """
    config_file = tmp_path / "flowcore.toml"
    config_file.write_text(config_content)
    
    # Change working directory to tmp_path temporarily
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    
    try:
        ctx = create_context(verbose=True)
        assert ctx.verbose is True
        assert ctx.server_url == "http://remote-server:9000"
        assert ctx.execution_mode == "remote"
        assert ctx.project_root == tmp_path
        assert ctx.config["project"]["name"] == "test-project"
    finally:
        os.chdir(original_cwd)
