import logging
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.pipeline.execution_step import ExecutionStep
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.dependencies.node import Node
from flowcore.models.operational.execution import ExecutionRun
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.plugins.manager import PluginManager
from flowcore.engine.executor.local import LocalExecutor
from flowcore.engine.runner.engine import EngineRunner
from flowcore.engine.state.memory import InMemoryStateStore
from typing import Any, Dict, Iterator, List, Optional
from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage

class MockIncrementalSource(SourcePlugin):
    @property
    def metadata(self) -> Any:
        class Meta:
            name = "mock_incremental"
            version = "1.0.0"
            author = "Test"
            description = "Mock Source"
            connector_type = "Source"
            flowcore_version_constraint = ">=1.0.0"
            capabilities = []
        return Meta()
        
    def check(self, config: Dict[str, Any]) -> bool: return True
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]: return []
    
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        last_id = state.get("last_id", 0) if state else 0
        for i in range(1, 4):
            current_id = last_id + i
            yield FlowCoreMessage(type=MessageType.RECORD, record=RecordMessage(stream="test", data={"id": current_id}))
            yield FlowCoreMessage(type=MessageType.STATE, state=StateMessage(state_data={"last_id": current_id}))

state_store = InMemoryStateStore()
step = ExecutionStep(step_id="source_1", connector_id="mock_incremental")
pv = PipelineVersion(id="pv1", pipeline_id="test_pipeline", version="1.0.0", steps=[step])
graph = DependencyGraph(nodes={"source_1": Node(node_id="source_1")}, edges=[])

pm = PluginManager()
pm._instance_registry["mock_incremental"] = MockIncrementalSource()

print("\n--- STARTING RUN 1 ---")
run1 = ExecutionRun(workspace_id="00000000-0000-0000-0000-000000000000", id="run1", pipeline_id="test_pipeline", pipeline_version_id="1.0.0", trigger_type="MANUAL")
coord1 = ExecutionCoordinator(pv, graph, state_store=state_store)
coord1.initialize_run(run1)
EngineRunner(coord1, pm, LocalExecutor(), state_store=state_store).run()
print(f"State after Run 1: {state_store.get_state('test_pipeline', 'source_1')}") 

print("\n--- STARTING RUN 2 (Incremental Sync) ---")
run2 = ExecutionRun(workspace_id="00000000-0000-0000-0000-000000000000", id="run2", pipeline_id="test_pipeline", pipeline_version_id="1.0.0", trigger_type="MANUAL")
coord2 = ExecutionCoordinator(pv, graph, state_store=state_store)
coord2.initialize_run(run2)
EngineRunner(coord2, pm, LocalExecutor(), state_store=state_store).run()
print(f"State after Run 2: {state_store.get_state('test_pipeline', 'source_1')}")
