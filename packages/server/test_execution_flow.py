import asyncio
import logging
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.models.execution import ExecutionRequest
from flowcore_server.dependencies.core import _repository_factory
from flowcore_server.application.engine_factory import DefaultExecutionEngineFactory
from flowcore.engine.plugins.manager import PluginManager
import uuid

async def test():
    logging.basicConfig(level=logging.DEBUG)
    
    uow = _repository_factory.get_unit_of_work()
    async with uow:
        # Get any pipeline
        from flowcore_server.repositories.postgres.pipeline import OrmPipeline, OrmPipelineVersion
        from sqlalchemy import select
        result = await uow.session.execute(select(OrmPipelineVersion).limit(1))
        pv = result.scalar_one_or_none()
        if not pv:
            print("No pipeline versions found.")
            return
            
        workspace_id = str(pv.workspace_id)
        
    from flowcore_server.dependencies.context import workspace_context
    workspace_context.set(workspace_id)
            
    print(f"Executing pipeline_id={pv.pipeline_id} version={pv.version_tag}")
        
    from flowcore_server.dependencies.engine import get_plugin_manager
    get_plugin_manager()
    
    # We need to mock auth dependency context
    # Let's bypass the API and call execution_service directly!
    
    from flowcore_server.application.background import BackgroundExecutionStrategy
    from fastapi import BackgroundTasks
    
    class SyncBackgroundStrategy(BackgroundExecutionStrategy):
        def __init__(self, bt):
            self.bt = bt
        def submit(self, run_id, func, *args, **kwargs):
            self.bt.add_task(func, *args, **kwargs)
            
    bt = BackgroundTasks()
    bg_strategy = SyncBackgroundStrategy(bt)
    
    from flowcore_server.dependencies.core import get_cancellation_strategy, get_event_dispatcher
    
    plugin_manager = PluginManager()
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    mock_plugins_dir = os.path.join(base_dir, "mock_plugins")
    plugin_manager.discover_plugins([mock_plugins_dir])
    
    svc = ExecutionService(
        uow=uow,
        engine_factory=DefaultExecutionEngineFactory(),
        cancellation_strategy=get_cancellation_strategy(),
        background_strategy=bg_strategy,
        plugin_manager=get_plugin_manager(),
        event_dispatcher=get_event_dispatcher()
    )
    
    run = await svc.start_execution(
        pipeline_id=str(pv.pipeline_id),
        version=pv.version_tag,
        trigger_type="TEST",
        parameters={}
    )
    
    print(f"Run started: {run.id}")
    print(f"Run steps: {run.steps}")
    
    # Run background tasks manually
    for task in bt.tasks:
        await task.func(*task.args, **task.kwargs)
        
    # Check dataset lineage
    async with uow:
        from flowcore_server.repositories.postgres.lineage import OrmDataset, OrmLineageEdge
        from sqlalchemy import select
        datasets = await uow.session.execute(select(OrmDataset))
        edges = await uow.session.execute(select(OrmLineageEdge))
        print("Datasets:", [d.name for d in datasets.scalars()])
        print("Edges:", len(edges.scalars().all()))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
