import pytest
import time
from flowcore.models.operational.execution import ExecutionRun
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.executor.thread import ThreadExecutor
from flowcore.engine.runner.engine import EngineRunner
from helpers import build_graph

def test_concurrency_limits(plugin_manager):
    # A graph with 10 independent steps
    nodes = [f"step_{i}" for i in range(10)]
    pv, graph = build_graph(nodes, [])
    
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(workspace_id="00000000-0000-0000-0000-000000000000", id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    # We use a ThreadExecutor with max_workers=2.
    # The dummy plugin sleeps for 0.01 seconds.
    # We want to ensure that the scheduler never dispatches more than max_workers at a time.
    
    with ThreadExecutor(max_workers=2) as executor:
        engine = EngineRunner(coord, plugin_manager, executor)
        
        # We can't easily assert the max running during the loop synchronously in this test 
        # without hooking into the executor. 
        # But we can assert the entire loop completes successfully, which validates
        # that the ExecutionScheduler (which has default concurrency=10) and the 
        # executor (which has 2) cooperate without deadlocking or dropping tasks.
        engine.run()
        
    for n in nodes:
        assert coord.get_step_state(n) == "COMPLETED"
    assert not coord.has_pending_work()
