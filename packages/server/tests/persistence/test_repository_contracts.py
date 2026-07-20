import pytest
import uuid
from flowcore_shared.schemas.pipeline import Pipeline, PipelineVersion
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState

@pytest.mark.asyncio
async def test_pipeline_crud_contract(any_uow):
    uow = any_uow
    
    # Create Pipeline
    p = Pipeline(
        id=str(uuid.uuid4()),
        name="test_pipeline",
        owner="data_team",
        description="test",
        tags=["etl"]
    )
    
    created = await uow.pipelines.create_pipeline(p)
    assert created.id == p.id
    assert created.name == "test_pipeline"
    
    # Read Pipeline
    fetched = await uow.pipelines.get_pipeline(p.id)
    assert fetched is not None
    assert fetched.name == "test_pipeline"
    assert fetched.owner == "data_team"
    
    # List Pipelines
    listed = await uow.pipelines.list_pipelines()
    assert len([x for x in listed if x.id == p.id]) == 1
    
    # Fetch by name
    fetched_name = await uow.pipelines.get_pipeline_by_name("test_pipeline")
    assert fetched_name is not None
    assert fetched_name.id == p.id
    
    # Missing by name
    assert await uow.pipelines.get_pipeline_by_name("nonexistent") is None
    
    # Create Pipeline Version
    pv = PipelineVersion(
        id=str(uuid.uuid4()), 
        pipeline_id=p.id, 
        version="v1.0"
    )
    await uow.pipelines.create_pipeline_version(pv)
    
    # Fetch Pipeline Version
    fetched_pv = await uow.pipelines.get_pipeline_version(p.id, "v1.0")
    assert fetched_pv is not None
    assert fetched_pv.id == pv.id
    
    # Fetch Pipeline Version by ID
    fetched_pv_id = await uow.pipelines.get_pipeline_version_by_id(pv.id)
    assert fetched_pv_id is not None
    assert fetched_pv_id.version == "v1.0"
    
    # Delete Pipeline
    deleted = await uow.pipelines.delete_pipeline(p.id)
    assert deleted is True
    
    # Fetch again (should be soft deleted or removed)
    fetched_after = await uow.pipelines.get_pipeline(p.id)
    assert fetched_after is None
    
    # False delete
    assert await uow.pipelines.delete_pipeline(str(uuid.uuid4())) is False

@pytest.mark.asyncio
async def test_execution_run_contract(any_uow):
    uow = any_uow
    
    # Setup Pipeline & Version
    p = Pipeline(id=str(uuid.uuid4()), name="exec_test", owner="dev")
    await uow.pipelines.create_pipeline(p)
    
    pv = PipelineVersion(
        id=str(uuid.uuid4()), 
        pipeline_id=p.id, 
        version="v1.0"
    )
    await uow.pipelines.create_pipeline_version(pv)
    
    # Create Execution Run
    run = ExecutionRun(
        id=str(uuid.uuid4()),
        pipeline_id=p.id,
        pipeline_version_id=pv.id,
        status=ExecutionState.PENDING,
        trigger_type="MANUAL"
    )
    
    created = await uow.executions.create_run(run)
    assert created.id == run.id
    
    # Update Status
    await uow.executions.update_run_status(run.id, ExecutionState.RUNNING)
    
    # Fetch Run
    fetched = await uow.executions.get_run(run.id)
    assert fetched is not None
    assert fetched.status == ExecutionState.RUNNING
    
    # Missing Run
    assert await uow.executions.get_run(str(uuid.uuid4())) is None
    
    # False update
    assert await uow.executions.update_run_status(str(uuid.uuid4()), ExecutionState.FAILED) is False
    
    # Save (Upsert) Run
    fetched = fetched.model_copy(update={"trigger_type": "SCHEDULED"}) # Modify via mock
    saved = await uow.executions.save(fetched)
    assert saved.trigger_type == "SCHEDULED"
    
    # List Runs
    runs = await uow.executions.list_runs_for_pipeline(p.id)
    assert len(runs) == 1
    assert runs[0].id == run.id
