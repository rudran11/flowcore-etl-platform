import pytest
import os
import tempfile
from typing import List, Tuple
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph
from flowcore_shared.schemas.dependencies.node import Node
from flowcore_shared.schemas.dependencies.edge import Edge
from flowcore_engine.plugins.manager import PluginManager

DUMMY_PLUGIN_CODE = """
import time
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType

class DummyPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="dummy",
            name="Dummy",
            version="1.0.0",
            plugin_type=PluginType.CONNECTOR,
            author="Test",
            description="Dummy"
        )
        
    def execute(self, context: Any) -> Any:
        time.sleep(0.01)
        return f"Completed {context.step_id}"
"""

FAULTY_PLUGIN_CODE = """
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore_engine.exceptions.plugin import FatalPluginError, RecoverablePluginError

class FaultyPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="faulty",
            name="Faulty",
            version="1.0.0",
            plugin_type=PluginType.CONNECTOR,
            author="Test",
            description="Faulty"
        )
        
    def execute(self, context: Any) -> Any:
        step_id = context.step_id
        if "fatal" in step_id:
            raise FatalPluginError("Fatal error")
        elif "retry" in step_id:
            # Simulate a timeout or network error that succeeds on retry attempt 1
            if context.retry_attempt == 0:
                raise RecoverablePluginError("Transient error")
            return "Recovered"
        return "Success"
"""

@pytest.fixture
def plugin_manager():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "dummy.py"), "w") as f:
            f.write(DUMMY_PLUGIN_CODE)
        with open(os.path.join(temp_dir, "faulty.py"), "w") as f:
            f.write(FAULTY_PLUGIN_CODE)
            
        manager = PluginManager()
        manager.discover_plugins([temp_dir])
        yield manager


