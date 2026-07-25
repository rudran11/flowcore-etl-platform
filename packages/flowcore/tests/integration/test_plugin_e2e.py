import pytest
from flowcore.models.operational.execution import ExecutionRun
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.executor.local import LocalExecutor
from flowcore.engine.runner.engine import EngineRunner
from helpers import build_graph

def test_plugin_e2e(plugin_manager):
    # This validates that plugin loading and execution works correctly natively.
    # The plugin manager discovers 'dummy', provides it to the engine, which injects RuntimeContext.
    pv, graph = build_graph(["A"], [])
    
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(workspace_id="00000000-0000-0000-0000-000000000000", id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    with LocalExecutor() as executor:
        engine = EngineRunner(coord, plugin_manager, executor)
        engine.run()
        
    assert coord.get_step_state("A") == "COMPLETED"
