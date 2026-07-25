# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import sys
from pathlib import Path

# Add shared and engine to path so pytest can find them in this bare environment
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root / "shared"))
sys.path.insert(0, str(root / "engine"))

from typer.testing import CliRunner
from flowcore_cli.main import app

runner = CliRunner()

VALID_YAML = """
version: "1.0"
pipeline:
  name: customer_etl
  description: Extract and load customers
  owner: test_owner
steps:
  - step_id: extract_customers
    connector_id: console
    parameters:
      message: "extracting"
  - step_id: extract_orders
    connector_id: console
    parameters:
      message: "extracting"
  - step_id: transform_customers
    connector_id: console
    depends_on: ["extract_customers"]
    parameters:
      message: "transform"
  - step_id: transform_orders
    connector_id: console
    depends_on: ["extract_orders"]
    parameters:
      message: "transform"
  - step_id: join_data
    connector_id: console
    depends_on: ["transform_customers", "transform_orders"]
    parameters:
      message: "join"
  - step_id: load_warehouse
    connector_id: console
    depends_on: ["join_data"]
    parameters:
      message: "load"
"""

INVALID_YAML = """
version: "2.0" # Invalid version
pipeline:
  name: customer_etl
  owner: test_owner
steps: []
"""

CYCLE_YAML = """
version: "1.0"
pipeline:
  name: cycle_etl
  owner: test_owner
steps:
  - step_id: step_a
    connector_id: console
    depends_on: ["step_b"]
    parameters: {message: "a"}
  - step_id: step_b
    connector_id: console
    depends_on: ["step_a"]
    parameters: {message: "b"}
"""

def setup_dummy_project(tmp_path):
    config = """
[project]
name = "test"

[server]
url = "http://localhost:8000"

[execution]
mode = "local"
    """
    (tmp_path / "flowcore.toml").write_text(config)
    
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir(exist_ok=True)
    plugin_code = """
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType

class ConsolePlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="console",
            name="Console Plugin",
            version="1.0.0",
            description="A dummy plugin",
            author="test",
            plugin_type=PluginType.CONNECTOR
        )
        
    def execute(self, runtime_context) -> None:
        pass
"""
    (plugins_dir / "console.py").write_text(plugin_code)

def test_validate_success(tmp_path):
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    setup_dummy_project(tmp_path)
    
    pipeline_file = tmp_path / "valid.yaml"
    pipeline_file.write_text(VALID_YAML)
    
    result = runner.invoke(app, ["validate", str(pipeline_file)])
    assert result.exit_code == 0
    assert "Validation successful" in result.stdout
    os.chdir(original_cwd)

def test_validate_dry_run(tmp_path):
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    setup_dummy_project(tmp_path)
    
    pipeline_file = tmp_path / "valid.yaml"
    pipeline_file.write_text(VALID_YAML)
    
    result = runner.invoke(app, ["validate", str(pipeline_file), "--dry-run"])
    assert result.exit_code == 0
    assert "Layer 1" in result.stdout
    assert "extract_customers" in result.stdout
    assert "Layer 2" in result.stdout
    assert "Layer 4" in result.stdout
    assert "load_warehouse" in result.stdout
    os.chdir(original_cwd)

def test_validate_invalid_schema(tmp_path):
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    setup_dummy_project(tmp_path)
    
    pipeline_file = tmp_path / "invalid.yaml"
    pipeline_file.write_text(INVALID_YAML)
    
    result = runner.invoke(app, ["validate", str(pipeline_file)])
    assert result.exit_code == 1
    assert "Unsupported DSL version" in result.stdout
    os.chdir(original_cwd)

def test_validate_cycle(tmp_path):
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    setup_dummy_project(tmp_path)
    
    pipeline_file = tmp_path / "cycle.yaml"
    pipeline_file.write_text(CYCLE_YAML)
    
    result = runner.invoke(app, ["validate", str(pipeline_file)])
    assert result.exit_code == 1
    assert "Dependency Error" in result.stdout
    assert "contains a cycle" in result.stdout
    os.chdir(original_cwd)
