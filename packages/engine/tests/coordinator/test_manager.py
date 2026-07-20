import pytest
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph
from flowcore_shared.schemas.dependencies.node import Node
from flowcore_shared.schemas.dependencies.edge import Edge
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.exceptions.plugin import FatalPluginError, RecoverablePluginError

def _build_test_graph_and_pipeline(edges_def: list[tuple[str, str]]):
    nodes = set()
    for s, t in edges_def:
        nodes.add(s)
        nodes.add(t)
    
    steps = [ExecutionStep(step_id=n, connector_id="test_conn") for n in nodes]
    pv = PipelineVersion(
        id="pv1",
        pipeline_id="pipe1",
        version="1.0.0",
        steps=steps
    )
    
    graph_nodes = {n: Node(node_id=n) for n in nodes}
    graph_edges = [Edge(source=s, target=t) for s, t in edges_def]
    graph = DependencyGraph(nodes=graph_nodes, edges=graph_edges)
    
    return pv, graph

def test_linear_graph_orchestration():
    pv, graph = _build_test_graph_and_pipeline([("A", "B"), ("B", "C")])
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    
    run = coord.initialize_run(run)
    assert run.status == ExecutionState.QUEUED
    assert coord.get_step_state("A") == ExecutionState.QUEUED
    assert coord.get_step_state("B") == ExecutionState.PENDING
    
    assert coord.has_pending_work()
    
    step_a = coord.get_next_runnable_step()
    assert step_a == "A"
    
    coord.on_step_started("A")
    assert coord.get_step_state("A") == ExecutionState.RUNNING
    
    coord.on_step_completed("A")
    assert coord.get_step_state("A") == ExecutionState.COMPLETED
    assert coord.get_step_state("B") == ExecutionState.QUEUED
    
    step_b = coord.get_next_runnable_step()
    assert step_b == "B"
    coord.on_step_started("B")
    coord.on_step_completed("B")
    
    step_c = coord.get_next_runnable_step()
    assert step_c == "C"
    coord.on_step_started("C")
    coord.on_step_completed("C")
    
    assert not coord.has_pending_work()

def test_diamond_dag_orchestration():
    # A -> B, A -> C, B -> D, C -> D
    pv, graph = _build_test_graph_and_pipeline([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    
    run = coord.initialize_run(run)
    step_a = coord.get_next_runnable_step()
    coord.on_step_started(step_a)
    coord.on_step_completed(step_a)
    
    # B and C should now be queued
    step1 = coord.get_next_runnable_step()
    step2 = coord.get_next_runnable_step()
    assert {step1, step2} == {"B", "C"}
    
    # D is blocked
    assert coord.get_next_runnable_step() is None
    
    # Complete B, D should still be blocked waiting for C
    coord.on_step_started("B")
    coord.on_step_completed("B")
    assert coord.get_next_runnable_step() is None
    assert coord.get_step_state("D") == ExecutionState.PENDING
    
    # Complete C, D should unblock
    coord.on_step_started("C")
    coord.on_step_completed("C")
    
    step_d = coord.get_next_runnable_step()
    assert step_d == "D"
    assert coord.get_step_state("D") == ExecutionState.QUEUED

def test_fatal_plugin_error_fail_fast():
    pv, graph = _build_test_graph_and_pipeline([("A", "B")])
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    
    run = coord.initialize_run(run)
    step_a = coord.get_next_runnable_step()
    coord.on_step_started(step_a)
    
    # Fail A with fatal error
    error = FatalPluginError("Bad auth")
    backoff = coord.on_step_failed(step_a, error)
    
    assert backoff is None
    assert coord.get_step_state("A") == ExecutionState.FAILED
    assert coord.get_step_state("B") == ExecutionState.PENDING
    
    # Queue is empty, B is stuck
    assert coord.get_next_runnable_step() is None
    assert not coord.has_pending_work()

def test_recoverable_plugin_error():
    pv, graph = _build_test_graph_and_pipeline([("A", "B")])
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    
    run = coord.initialize_run(run)
    step_a = coord.get_next_runnable_step()
    coord.on_step_started(step_a)
    
    error = RecoverablePluginError("Timeout")
    backoff = coord.on_step_failed(step_a, error)
    
    assert backoff is not None
    assert coord.get_step_state("A") == ExecutionState.RETRYING
    
    # Since it's RETRYING, the task slot was freed, but it's not yet requeued.
    # The external executor loop would sleep `backoff` and re-submit it (future implementation).
    assert not coord.has_pending_work() # Queue is empty
