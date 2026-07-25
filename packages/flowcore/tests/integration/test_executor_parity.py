import pytest
from flowcore.models.operational.execution import ExecutionRun
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.executor.thread import ThreadExecutor
from flowcore.engine.executor.local import LocalExecutor
from flowcore.engine.runner.engine import EngineRunner
from helpers import build_graph

def run_with_executor(plugin_manager, executor_class, kwargs):
    pv, graph = build_graph(["A", "B", "C"], [("A", "B"), ("B", "C")])
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(workspace_id="00000000-0000-0000-0000-000000000000", id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    if executor_class == ThreadExecutor:
        with executor_class(**kwargs) as executor:
            engine = EngineRunner(coord, plugin_manager, executor)
            engine.run()
    else:
        with executor_class() as executor:
            engine = EngineRunner(coord, plugin_manager, executor)
            engine.run()
            
    return coord

def test_executor_parity(plugin_manager):
    # Run identical pipeline through both executors
    coord_thread = run_with_executor(plugin_manager, ThreadExecutor, {"max_workers": 2})
    coord_local = run_with_executor(plugin_manager, LocalExecutor, {})
    
    # Assert identical final state
    assert coord_thread.get_step_state("A") == coord_local.get_step_state("A") == "COMPLETED"
    assert coord_thread.get_step_state("B") == coord_local.get_step_state("B") == "COMPLETED"
    assert coord_thread.get_step_state("C") == coord_local.get_step_state("C") == "COMPLETED"
