import pytest
import uuid
from flowcore_shared.schemas.pipeline import Pipeline, PipelineVersion
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState

from flowcore_shared.schemas.auth.organization import Organization
from flowcore_shared.schemas.auth.workspace import Workspace

async def setup_dummy_workspace(uow):
    org_id = "00000000-0000-0000-0000-000000000001"
    ws_id = "00000000-0000-0000-0000-000000000000"
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if await uow.organizations.get(org_id) is None:
        await uow.organizations.create(Organization(id=org_id, name="Test Org", slug="test-org", created_at=now, updated_at=now))
    if await uow.workspaces.get(ws_id) is None:
        await uow.workspaces.create(Workspace(id=ws_id, organization_id=org_id, name="Test WS", slug="test-ws", created_at=now, updated_at=now))
    await uow.commit()

@pytest.mark.asyncio
async def test_pipeline_crud_contract(any_uow):
    uow = any_uow
    await setup_dummy_workspace(uow)
    
    # Create Pipeline
    p = Pipeline(
        id=str(uuid.uuid4()),
        workspace_id=str(uuid.uuid4()),
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
    async with any_uow as uow:
        await setup_dummy_workspace(uow)
        pipe_uuid = str(uuid.uuid4())
        await uow.pipelines.create_pipeline(Pipeline(id=pipe_uuid, workspace_id=str(uuid.uuid4()), name="test", owner="owner"))
        
        pv = PipelineVersion(
            id=str(uuid.uuid4()),
            pipeline_id=pipe_uuid,
            version="1.0.0",
            steps=[]
        )
        await uow.pipelines.create_pipeline_version(pv)
    
    # Create Execution Run
    run = ExecutionRun(
        id=str(uuid.uuid4()),
        workspace_id=str(uuid.uuid4()),
        pipeline_id=pipe_uuid,
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
    runs = await uow.executions.list_runs_for_pipeline(pipe_uuid)
    assert len(runs) == 1
    assert runs[0].id == run.id

@pytest.mark.asyncio
async def test_dashboard_aggregations(any_uow):
    """Test dashboard aggregation methods on both in-memory and postgres UoWs."""
    from datetime import datetime, timedelta
    
    # Needs a pipeline version due to foreign keys in postgres
    pipe_uuid = str(uuid.uuid4())
    pv = PipelineVersion(
        id=str(uuid.uuid4()),
        pipeline_id=pipe_uuid,
        version="1.0.0",
        steps=[]
    )
    
    async with any_uow as uow:
        await setup_dummy_workspace(uow)
        await uow.pipelines.create_pipeline(Pipeline(id=pipe_uuid, workspace_id=str(uuid.uuid4()), name="t1", owner="u"))
        await uow.pipelines.create_pipeline_version(pv)
        
        now = datetime.utcnow()
        ws_id = str(uuid.uuid4())
        # Create 3 runs: 1 running, 1 completed (duration 1 min), 1 failed (duration 5 min)
        r1 = ExecutionRun(id=str(uuid.uuid4()), workspace_id=ws_id, pipeline_id=pipe_uuid, pipeline_version_id=pv.id, status=ExecutionState.RUNNING, start_time=now - timedelta(minutes=10), trigger_type="MANUAL")
        r2 = ExecutionRun(id=str(uuid.uuid4()), workspace_id=ws_id, pipeline_id=pipe_uuid, pipeline_version_id=pv.id, status=ExecutionState.COMPLETED, start_time=now - timedelta(minutes=5), end_time=now - timedelta(minutes=4), trigger_type="MANUAL")
        r3 = ExecutionRun(id=str(uuid.uuid4()), workspace_id=ws_id, pipeline_id=pipe_uuid, pipeline_version_id=pv.id, status=ExecutionState.FAILED, start_time=now - timedelta(minutes=6), end_time=now - timedelta(minutes=1), trigger_type="MANUAL")
        
        await uow.executions.create_run(r1)
        await uow.executions.create_run(r2)
        await uow.executions.create_run(r3)
        await uow.commit()

        # Test count_pipelines
        assert await uow.pipelines.count_pipelines() >= 1

        # Test execution_summary
        summary = await uow.executions.execution_summary()
        assert summary[ExecutionState.RUNNING.value] >= 1
        assert summary[ExecutionState.COMPLETED.value] >= 1
        assert summary[ExecutionState.FAILED.value] >= 1
        assert summary[ExecutionState.CANCELLED.value] >= 0
        assert summary[ExecutionState.QUEUED.value] >= 0

        # Test daily_execution_counts
        counts = await uow.executions.daily_execution_counts(days=7)
        assert len(counts) == 7
        today_stats = counts[-1] # the last one is today
        assert today_stats[ExecutionState.COMPLETED.value] >= 1
        assert today_stats[ExecutionState.FAILED.value] >= 1

        # Test average_duration_ms
        # r2 completed in 1 min (60000ms)
        avg = await uow.executions.average_duration_ms()
        assert avg == 60000.0

        # Test recent_runs
        recent = await uow.executions.recent_runs(limit=10)
        assert len(recent) >= 3
