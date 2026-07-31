import pytest
from typing import Any, Dict, Iterator, List, Optional
from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.pipeline.execution_step import ExecutionStep
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.dependencies.node import Node
from flowcore.models.dependencies.edge import Edge
from flowcore.models.operational.execution import ExecutionRun
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.plugins.manager import PluginManager
from flowcore.engine.executor.local import LocalExecutor
from flowcore.engine.runner.engine import EngineRunner
from flowcore.engine.state.memory import InMemoryStateStore

class MockIncrementalSource(SourcePlugin):
    """A mock source that reads starting from a state cursor and yields new state."""
    
    @property
    def metadata(self) -> Any:
        class MockMeta:
            name = "mock_incremental"
            version = "1.0.0"
            author = "test"
            description = "mock"
            connector_type = "Source"
            flowcore_version_constraint = ">=1.0.0"
            capabilities = []
        return MockMeta()
        
    def check(self, config: Dict[str, Any]) -> bool:
        return True
        
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        last_id = state.get("last_id", 0) if state else 0
        
        # Yield 3 records starting from last_id + 1
        for i in range(1, 4):
            current_id = last_id + i
            yield FlowCoreMessage(
                type=MessageType.RECORD,
                record=RecordMessage(stream="test_stream", data={"id": current_id})
            )
            
            # Emit state after every record
            yield FlowCoreMessage(
                type=MessageType.STATE,
                state=StateMessage(state_data={"last_id": current_id})
            )

def _setup_pipeline() -> tuple[PipelineVersion, DependencyGraph, ExecutionRun]:
    step = ExecutionStep(step_id="source_1", connector_id="mock_incremental")
    pv = PipelineVersion(
        id="pv1",
        pipeline_id="pipe1",
        version="1.0.0",
        steps=[step]
    )
    
    graph = DependencyGraph(
        nodes={"source_1": Node(node_id="source_1")},
        edges=[]
    )
    
    run = ExecutionRun(
        workspace_id="00000000-0000-0000-0000-000000000000",
        id="run1",
        pipeline_id="pipe1",
        pipeline_version_id="1.0.0",
        trigger_type="MANUAL"
    )
    
    return pv, graph, run

def test_state_persistence_and_incremental_sync():
    state_store = InMemoryStateStore()
    
    # --- RUN 1 ---
    pv, graph, run1 = _setup_pipeline()
    
    # Mock plugin manager to return our Mock source
    pm = PluginManager()
    pm._instance_registry["mock_incremental"] = MockIncrementalSource()
    
    coord1 = ExecutionCoordinator(pv, graph, state_store=state_store)
    coord1.initialize_run(run1)
    
    runner1 = EngineRunner(coord1, pm, LocalExecutor(), state_store=state_store)
    runner1.run()
    
    # Assert state was persisted to store
    persisted_state = state_store.get_state("pipe1", "source_1")
    assert persisted_state is not None
    assert persisted_state["last_id"] == 3
    
    # --- RUN 2 (Incremental) ---
    _, _, run2 = _setup_pipeline()
    run2 = ExecutionRun(
        workspace_id="00000000-0000-0000-0000-000000000000",
        id="run2",
        pipeline_id="pipe1",
        pipeline_version_id="1.0.0",
        trigger_type="MANUAL"
    )
    
    coord2 = ExecutionCoordinator(pv, graph, state_store=state_store)
    coord2.initialize_run(run2)
    
    runner2 = EngineRunner(coord2, pm, LocalExecutor(), state_store=state_store)
    runner2.run()
    
    # Assert state was injected and updated
    persisted_state_2 = state_store.get_state("pipe1", "source_1")
    assert persisted_state_2 is not None
    assert persisted_state_2["last_id"] == 6
