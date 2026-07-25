import pytest
import asyncio
from datetime import datetime, timezone
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.repositories.in_memory.uow import InMemoryUnitOfWork
from flowcore_server.application.engine_factory import DefaultExecutionEngineFactory
from flowcore_server.application.cancellation import DefaultCancellationStrategy
from flowcore_server.application.background import BackgroundExecutionStrategy
from flowcore.engine.plugins.manager import PluginManager
from flowcore_server.application.dispatchers.in_memory import InMemoryEventDispatcher
from flowcore_shared.schemas.pipeline.pipeline import Pipeline
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_shared.events.domain import (
    PipelineExecutionStarted,
    PipelineExecutionCompleted,
    PipelineExecutionFailed,
    RunCancelled
)

class MockBackgroundStrategy:
    def submit(self, run_id, func, *args, **kwargs):
        pass
    def shutdown(self):
        pass

@pytest.fixture
def uow():
    return InMemoryUnitOfWork()

@pytest.fixture
def dispatcher():
    return InMemoryEventDispatcher()

@pytest.fixture
def service(uow, dispatcher):
    return ExecutionService(
        uow=uow,
        engine_factory=DefaultExecutionEngineFactory(),
        cancellation_strategy=DefaultCancellationStrategy(),
        background_strategy=MockBackgroundStrategy(),
        plugin_manager=PluginManager(),
        event_dispatcher=dispatcher
    )

@pytest.mark.asyncio
async def test_event_published_after_successful_commit(service, uow, dispatcher):
    # Setup
    async with uow:
        p = Pipeline(id="test-pipe", name="test", owner="test", workspace_id="test-workspace")
        await uow.pipelines.create_pipeline(p)
        pv = PipelineVersion(id="test-version-id", pipeline_id="test-pipe", version="1.0", steps=[])
        await uow.pipelines.create_pipeline_version(pv)
        await uow.commit()

    # Execute
    run = await service.start_execution("test-pipe", "1.0", "MANUAL", {})
    
    # Assert
    assert len(dispatcher.published_events) == 1
    event = dispatcher.published_events[0]
    assert isinstance(event, PipelineExecutionStarted)
    assert event.run_id == run.id
    assert event.pipeline_id == "test-pipe"
    assert event.pipeline_version_id == "test-version-id"
    
    # Check metadata
    assert event.event_id is not None
    assert event.occurred_at is not None
    assert event.occurred_at.tzinfo == timezone.utc

@pytest.mark.asyncio
async def test_no_event_published_after_rollback(service, uow, dispatcher):
    # Force a failure in uow.commit() by raising an exception, or by crashing before commit
    # Since start_execution catches nothing if UoW fails, we mock uow.commit to raise.
    async with uow:
        p = Pipeline(id="test-pipe-rb", name="test", owner="test", workspace_id="test-workspace")
        await uow.pipelines.create_pipeline(p)
        pv = PipelineVersion(id="test-version-id-rb", pipeline_id="test-pipe-rb", version="1.0", steps=[])
        await uow.pipelines.create_pipeline_version(pv)
        await uow.commit()

    original_commit = service.uow.commit
    async def failing_commit():
        raise RuntimeError("DB Connection Failed")
    
    service.uow.commit = failing_commit

    with pytest.raises(RuntimeError):
        await service.start_execution("test-pipe-rb", "1.0", "MANUAL", {})

    assert len(dispatcher.published_events) == 0

@pytest.mark.asyncio
async def test_events_emitted_in_correct_order_and_fifo(service, uow, dispatcher):
    # Setup
    async with uow:
        p = Pipeline(id="test-pipe", name="test", owner="test", workspace_id="test-workspace")
        await uow.pipelines.create_pipeline(p)
        pv = PipelineVersion(id="test-version-id", pipeline_id="test-pipe", version="1.0", steps=[])
        await uow.pipelines.create_pipeline_version(pv)
        await uow.commit()

    # Start
    run = await service.start_execution("test-pipe", "1.0", "MANUAL", {})
    
    # Cancel
    await service.cancel_execution(run.id)
    
    # Complete
    await service.complete_execution(run.id)
    
    # Fail
    await service.fail_execution(run.id, "Test Error")

    # Verify FIFO order
    assert len(dispatcher.published_events) == 4
    
    assert isinstance(dispatcher.published_events[0], PipelineExecutionStarted)
    assert isinstance(dispatcher.published_events[1], RunCancelled)
    assert isinstance(dispatcher.published_events[2], PipelineExecutionCompleted)
    
    failed_event = dispatcher.published_events[3]
    assert isinstance(failed_event, PipelineExecutionFailed)
    assert failed_event.error_message == "Test Error"
