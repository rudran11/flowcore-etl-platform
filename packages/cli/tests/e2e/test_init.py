# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
from pathlib import Path
from typer.testing import CliRunner
from flowcore_cli.main import app
import tomlkit

runner = CliRunner()

def test_cli_init_command(tmp_path):
    # Change working directory to tmp_path temporarily
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    
    try:
        result = runner.invoke(app, ["init", "my_new_project"])
        
        assert result.exit_code == 0
        assert "Initializing FlowCore project" in result.stdout
        assert "Created project directory" in result.stdout
        
        # Verify structure
        project_dir = tmp_path / "my_new_project"
        assert project_dir.exists()
        assert (project_dir / "pipelines").exists()
        assert (project_dir / "plugins").exists()
        
        # Verify config
        config_path = project_dir / "flowcore.toml"
        assert config_path.exists()
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = tomlkit.parse(f.read())
            assert config["project"]["name"] == "my_new_project"
            assert config["server"]["url"] == "http://localhost:8000"
            
    finally:
        os.chdir(original_cwd)
