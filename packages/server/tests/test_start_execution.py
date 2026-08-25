import asyncio
from flowcore_server.repositories.postgres.uow import AsyncSqlAlchemyUnitOfWork
import flowcore_server.dependencies.context as ctx
from flowcore_server.services.execution_service import ExecutionService
from flowcore.engine.plugins.manager import PluginManager
from flowcore_server.application.engine_factory import DefaultExecutionEngineFactory
from flowcore_server.application.cancellation import DefaultCancellationStrategy
from flowcore_server.application.background import FastAPIBackgroundStrategy
from flowcore_server.application.dispatchers.in_memory import InMemoryEventDispatcher
from fastapi import BackgroundTasks

async def main():
    pm = PluginManager()
    pm.discover_plugins(["../flowcore-shared/flowcore_shared/plugins"])
    
    ctx.workspace_context.set('00000000-0000-0000-0000-000000000000')
    
    uow = AsyncSqlAlchemyUnitOfWork()
    
    async with uow:
        pipelines = await uow.pipelines.list_pipelines()
        p = pipelines[0]
        versions = await uow.pipelines.list_pipeline_versions(p.id)
        v = versions[0]
        
    engine_factory = DefaultExecutionEngineFactory()
    cancellation_strategy = DefaultCancellationStrategy()
    bt = BackgroundTasks()
    background_strategy = FastAPIBackgroundStrategy(bt)
    event_dispatcher = InMemoryEventDispatcher()
    
    exec_service = ExecutionService(uow, engine_factory, cancellation_strategy, background_strategy, pm, event_dispatcher)
    
    print(f"Triggering pipeline {p.id}")
    
    try:
        run = await exec_service.start_execution(
            pipeline_id=str(p.id),
            version=str(v.version),
            trigger_type="TEST",
            parameters={},
            trigger_context=None
        )
        print("Run triggered:", run.id)
        
        # Execute the background tasks!
        for task in bt.tasks:
            # task is a BackgroundTask object
            if asyncio.iscoroutinefunction(task.func):
                await task.func(*task.args, **task.kwargs)
            else:
                task.func(*task.args, **task.kwargs)
                
    except Exception as e:
        print(f"Error triggering: {e}")
        import traceback
        traceback.print_exc()
        
    # Wait for completion
    for i in range(10):
        async with uow:
            r = await uow.executions.get_run(run.id)
            print(f"Status: {r.status}")
            if r.status.value in ['COMPLETED', 'FAILED']:
                print(f"Final error: {r.error_message}")
                break
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
