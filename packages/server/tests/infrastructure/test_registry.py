import pytest
from datetime import datetime
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.application.registry import InMemoryRunRegistry

def test_in_memory_registry():
    registry = InMemoryRunRegistry()
    
    run = ExecutionRun(
        id="run-1",
        pipeline_id="pipe-1",
        pipeline_version_id="ver-1",
        trigger_type="MANUAL"
    )
    
    registry.create_run(run)
    retrieved = registry.get_run("run-1")
    assert retrieved.id == "run-1"
    assert retrieved.status == ExecutionState.PENDING
    
    # Test duplicate creation
    with pytest.raises(ValueError, match="already exists"):
        registry.create_run(run)
        
    # Test get not found
    with pytest.raises(ValueError, match="not found"):
        registry.get_run("missing")
        
    # Test update
    updated_run = ExecutionRun(
        id="run-1",
        pipeline_id="pipe-1",
        pipeline_version_id="ver-1",
        trigger_type="MANUAL",
        status=ExecutionState.RUNNING,
        start_time=datetime.now()
    )
    registry.save(updated_run)
    retrieved2 = registry.get_run("run-1")
    assert retrieved2.status == ExecutionState.RUNNING
    
    # Test close
    registry.close() # Should not raise
