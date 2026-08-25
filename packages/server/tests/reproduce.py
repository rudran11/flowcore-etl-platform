import asyncio
from sqlalchemy import select
from flowcore_server.db.database import get_session
from flowcore_server.db.models import Workspace, Pipeline, PipelineVersion, ExecutionRun as OrmExecutionRun
from flowcore_server.repositories.postgres.uow import PostgresUnitOfWork
import flowcore_server.dependencies.context as ctx
from flowcore_server.services.execution_service import ExecutionService
from flowcore.engine.plugins.manager import PluginManager

async def main():
    pm = PluginManager()
    pm.discover_plugins("flowcore_shared.plugins")
    
    async for session in get_session():
        uow = PostgresUnitOfWork(session)
        w = await session.scalar(select(Workspace))
        if not w:
            print("No workspace found")
            return
        ctx.workspace_context.set(str(w.id))
        
        pipelines = await uow.pipelines.list_pipelines()
        if not pipelines:
            print("No pipelines found")
            return
            
        p = pipelines[0]
        versions = await uow.pipelines.list_versions(p.id)
        if not versions:
            print("No versions found")
            return
            
        v = versions[0]
        
        exec_service = ExecutionService(uow)
        print(f"Triggering execution for pipeline {p.id} version {v.id}")
        run = await exec_service.start_execution(p.id, str(v.id), "API", {}, None)
        print(f"Run ID: {run.id}")
        
        # Wait for the run to complete
        while True:
            r = await exec_service.get_execution(run.id)
            print(f"Status: {r.status}")
            if r.status.value in ['COMPLETED', 'FAILED']:
                print(f"Final error: {r.error_message}")
                break
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
