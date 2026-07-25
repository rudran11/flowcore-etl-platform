import asyncio
import logging
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.models.execution import ExecutionRequest
from flowcore_server.dependencies.core import get_repository_factory
from flowcore_server.application.engine_factory import DefaultExecutionEngineFactory
from flowcore.engine.plugins.manager import PluginManager

async def test():
    repo_factory = get_repository_factory()
    uow = repo_factory.get_unit_of_work()
    
    # We need a pipeline version first. 
    # Just list pipelines and get one.
    async with uow:
        # this won't work easily without a mock auth context
        pass

if __name__ == "__main__":
    asyncio.run(test())
