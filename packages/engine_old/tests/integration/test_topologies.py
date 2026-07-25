import pytest
from flowcore.models.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.executor.thread import ThreadExecutor
from flowcore_engine.runner.engine import EngineRunner
from helpers import build_graph

def test_linear_topology(plugin_manager):
    # A -> B -> C
    pv, graph = build_graph(["A", "B", "C"], [("A", "B"), ("B", "C")])
    
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    with ThreadExecutor(max_workers=2) as executor:
        engine = EngineRunner(coord, plugin_manager, executor)
        engine.run()
        
    assert coord.get_step_state("A") == ExecutionState.COMPLETED
    assert coord.get_step_state("B") == ExecutionState.COMPLETED
    assert coord.get_step_state("C") == ExecutionState.COMPLETED
    assert not coord.has_pending_work()

def test_diamond_topology(plugin_manager):
    # A -> B/C -> D
    pv, graph = build_graph(["A", "B", "C", "D"], [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    with ThreadExecutor(max_workers=4) as executor:
        engine = EngineRunner(coord, plugin_manager, executor)
        engine.run()
        
    assert coord.get_step_state("A") == ExecutionState.COMPLETED
    assert coord.get_step_state("B") == ExecutionState.COMPLETED
    assert coord.get_step_state("C") == ExecutionState.COMPLETED
    assert coord.get_step_state("D") == ExecutionState.COMPLETED
    assert not coord.has_pending_work()

def test_disconnected_topology(plugin_manager):
    # A -> B, C -> D (Two disconnected sub-DAGs)
    pv, graph = build_graph(["A", "B", "C", "D"], [("A", "B"), ("C", "D")])
    
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    with ThreadExecutor(max_workers=4) as executor:
        engine = EngineRunner(coord, plugin_manager, executor)
        engine.run()
        
    assert coord.get_step_state("A") == ExecutionState.COMPLETED
    assert coord.get_step_state("B") == ExecutionState.COMPLETED
    assert coord.get_step_state("C") == ExecutionState.COMPLETED
    assert coord.get_step_state("D") == ExecutionState.COMPLETED
    assert not coord.has_pending_work()
