import asyncio
from flowcore_server.dependencies.core import get_uow, init_dependencies
import flowcore_server.dependencies.context as ctx
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.application.execution_app import ExecutionApp
from flowcore.engine.plugins.manager import PluginManager

async def main():
    init_dependencies("postgres", "") # Need to pass connection string maybe? 
    uow = await get_uow()
    # Or just use the API!
