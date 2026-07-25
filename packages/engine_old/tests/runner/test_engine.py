import pytest
import os
import tempfile
import time
from typing import Any
from flowcore_shared.plugins.base import BasePlugin
from flowcore_shared.plugins.models import PluginMetadata
from flowcore_shared.plugins.enums import PluginType
from flowcore.models.pipeline.pipeline import Pipeline
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.pipeline.execution_step import ExecutionStep
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.plugins.manager import PluginManager
from flowcore_engine.executor.thread import ThreadExecutor
from flowcore_engine.runner.engine import EngineRunner

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
            plugin_id="dummy.connector",
            name="Dummy",
            version="1.0.0",
            plugin_type=PluginType.CONNECTOR,
            author="Test",
            description="Dummy"
        )
        
    def execute(self, context: Any) -> Any:
        time.sleep(0.1)
        return f"Completed {context.step_id}"
"""

def _build_complex_dag() -> (PipelineVersion, DependencyGraph):
    #           A
    #         /   \
    #        B     C
    #       / \   /
    #      D   E F
    #         \ /
    #          G
    
    steps = [
        ExecutionStep(step_id="A", connector_id="dummy.connector", depends_on=[]),
        ExecutionStep(step_id="B", connector_id="dummy.connector", depends_on=["A"]),
        ExecutionStep(step_id="C", connector_id="dummy.connector", depends_on=["A"]),
        ExecutionStep(step_id="D", connector_id="dummy.connector", depends_on=["B"]),
        ExecutionStep(step_id="E", connector_id="dummy.connector", depends_on=["B"]),
        ExecutionStep(step_id="F", connector_id="dummy.connector", depends_on=["C"]),
        ExecutionStep(step_id="G", connector_id="dummy.connector", depends_on=["E", "F"]),
    ]
    
    pv = PipelineVersion(
        id="pv1",
        pipeline_id="pipe1",
        version="1.0.0",
        steps=steps
    )
    
    from flowcore.models.dependencies.node import Node
    from flowcore.models.dependencies.edge import Edge
    
    nodes = {s.step_id: Node(node_id=s.step_id) for s in steps}
    edges = [
        Edge(source="A", target="B"),
        Edge(source="A", target="C"),
        Edge(source="B", target="D"),
        Edge(source="B", target="E"),
        Edge(source="C", target="F"),
        Edge(source="E", target="G"),
        Edge(source="F", target="G")
    ]
    graph = DependencyGraph(nodes=nodes, edges=edges)
    return pv, graph

def test_engine_runner_complex_dag():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "dummy.py"), "w") as f:
            f.write(DUMMY_PLUGIN_CODE)
            
        # 1. Setup Plugin Manager
        plugin_manager = PluginManager()
        plugin_manager.discover_plugins([temp_dir])
        
        # 2. Setup Coordinator
        pv, graph = _build_complex_dag()
        coordinator = ExecutionCoordinator(pv, graph)
        run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
        coordinator.initialize_run(run)
        
        # 3. Setup Executor
        with ThreadExecutor(max_workers=4) as executor:
            # 4. Setup Engine
            engine = EngineRunner(coordinator, plugin_manager, executor)
            
            # Run the DAG
            engine.run()
            
            # Verify states
            assert coordinator.get_step_state("A") == ExecutionState.COMPLETED
            assert coordinator.get_step_state("B") == ExecutionState.COMPLETED
            assert coordinator.get_step_state("C") == ExecutionState.COMPLETED
            assert coordinator.get_step_state("D") == ExecutionState.COMPLETED
            assert coordinator.get_step_state("E") == ExecutionState.COMPLETED
            assert coordinator.get_step_state("F") == ExecutionState.COMPLETED
            assert coordinator.get_step_state("G") == ExecutionState.COMPLETED
            
            # Queue should be empty
            assert not coordinator.has_pending_work()
