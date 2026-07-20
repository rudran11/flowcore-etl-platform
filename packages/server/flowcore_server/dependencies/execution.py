from fastapi import Depends
from flowcore_server.application.execution_app import ExecutionApp
from flowcore_server.services.execution_service import ExecutionService
from flowcore_server.dependencies.core import (
    get_run_registry,
    get_pipeline_repository,
    get_cancellation_strategy,
    get_engine_factory,
    get_background_strategy
)
from flowcore_server.dependencies.engine import get_plugin_manager

def get_execution_service(
    pipeline_repo = Depends(get_pipeline_repository),
    engine_factory = Depends(get_engine_factory),
    run_registry = Depends(get_run_registry),
    cancellation_strategy = Depends(get_cancellation_strategy),
    background_strategy = Depends(get_background_strategy),
    plugin_manager = Depends(get_plugin_manager)
) -> ExecutionService:
    return ExecutionService(
        pipeline_repo=pipeline_repo,
        engine_factory=engine_factory,
        run_registry=run_registry,
        cancellation_strategy=cancellation_strategy,
        background_strategy=background_strategy,
        plugin_manager=plugin_manager
    )

def get_execution_app(service: ExecutionService = Depends(get_execution_service)) -> ExecutionApp:
    return ExecutionApp(execution_service=service)
