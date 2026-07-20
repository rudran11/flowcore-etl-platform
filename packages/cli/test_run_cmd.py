import sys
import pathlib
import os

root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(root / "cli"))
sys.path.insert(0, str(root / "shared"))
sys.path.insert(0, str(root / "engine"))

test_run = root / "cli" / "test_run"
test_run.mkdir(exist_ok=True)

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

plugins_dir = test_run / "plugins"
plugins_dir.mkdir(exist_ok=True)

plugin_code = """
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore_engine.executor.models import ExecutionResult
import time

class DummyPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="dummy",
            name="Dummy Plugin",
            version="1.0.0",
            description="Dummy",
            author="test",
            plugin_type=PluginType.CONNECTOR
        )
        
    def execute(self, runtime_context):
        time.sleep(1.0)
        return {"status": "ok"}
"""
(plugins_dir / "dummy.py").write_text(plugin_code)

pipeline_code = """
version: '1.0'
pipeline:
  name: test_pipe
  owner: test
steps:
  - step_id: s1
    connector_id: dummy
  - step_id: s2
    connector_id: dummy
    depends_on: [s1]
"""
(test_run / "pipeline.yaml").write_text(pipeline_code)

config_code = """
[project]
name = "test"

[server]
url = "http://localhost:8000"

[execution]
mode = "local"
"""
(test_run / "flowcore.toml").write_text(config_code)

import flowcore_cli.main
os.chdir(str(test_run))
sys.argv = ["flowcore", "run", "pipeline.yaml"]
try:
    flowcore_cli.main.app()
except SystemExit as e:
    print(f"Exited with {e.code}")
