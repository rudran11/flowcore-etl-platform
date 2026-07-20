import pytest
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.executor.thread import ThreadExecutor
from flowcore_engine.runner.engine import EngineRunner
from helpers import build_graph

def test_stress_large_dag(plugin_manager):
    # Create a 200 node DAG: 10 parallel chains of 20 nodes
    nodes = []
    edges = []
    
    for chain_id in range(10):
        prev = None
        for step_idx in range(20):
            node_id = f"c{chain_id}_s{step_idx}"
            nodes.append(node_id)
            if prev:
                edges.append((prev, node_id))
            prev = node_id
            
    pv, graph = build_graph(nodes, edges)
    
    coord = ExecutionCoordinator(pv, graph)
    run = ExecutionRun(id="run1", pipeline_id="pipe1", pipeline_version_id="1.0.0", trigger_type="MANUAL")
    coord.initialize_run(run)
    
    with ThreadExecutor(max_workers=8) as executor:
        engine = EngineRunner(coord, plugin_manager, executor)
        engine.run()
        
    for n in nodes:
        assert coord.get_step_state(n) == "COMPLETED"
    assert not coord.has_pending_work()
