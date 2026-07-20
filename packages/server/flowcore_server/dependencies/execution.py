from fastapi import Depends
from flowcore_server.application.execution_app import ExecutionApp
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.dependencies.core import (
    get_uow,
    get_cancellation_strategy,
    get_engine_factory,
    get_background_strategy,
    get_event_dispatcher
)
from flowcore_server.dependencies.engine import get_plugin_manager
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.application.interfaces.dispatcher import AbstractEventDispatcher

def get_execution_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
    engine_factory = Depends(get_engine_factory),
    cancellation_strategy = Depends(get_cancellation_strategy),
    background_strategy = Depends(get_background_strategy),
    plugin_manager = Depends(get_plugin_manager),
    event_dispatcher: AbstractEventDispatcher = Depends(get_event_dispatcher)
) -> ExecutionService:
    return ExecutionService(
        uow=uow,
        engine_factory=engine_factory,
        cancellation_strategy=cancellation_strategy,
        background_strategy=background_strategy,
        plugin_manager=plugin_manager,
        event_dispatcher=event_dispatcher
    )

def get_execution_app(service: ExecutionService = Depends(get_execution_service)) -> ExecutionApp:
    return ExecutionApp(execution_service=service)
