from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from flowcore.engine.exceptions.plugin import PluginLoadError
from flowcore_server.application.exceptions import ResourceNotFoundError
from .config.settings import settings
from .api.v1.router import api_router
from .exceptions.handlers import (
    plugin_load_error_handler,
    validation_error_handler,
    value_error_handler,
    global_exception_handler,
    resource_not_found_handler
)

from contextlib import asynccontextmanager
from flowcore_server.dependencies.core import _repository_factory
from flowcore_server.services.seed import seed_default_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup seed logic
    uow = _repository_factory.get_unit_of_work()
    await seed_default_data(uow)
    yield
    # Cleanup on shutdown

def create_app() -> FastAPI:
    app = FastAPI(
        title="FlowCore Execution API",
        version="1.0.0",
        description="REST API gateway and control plane for FlowCore.",
        lifespan=lifespan
    )

    # Middleware (Last added = Outermost/First executed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from flowcore_server.middleware.tracing import TracingMiddleware
    from flowcore_server.middleware.workspace import WorkspaceMiddleware
    
    app.add_middleware(WorkspaceMiddleware)
    app.add_middleware(TracingMiddleware)

    # Exception Handlers
    app.add_exception_handler(PluginLoadError, plugin_load_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Routers
    app.include_router(api_router)

    return app

from .config.logging_setup import setup_logging
setup_logging()

app = create_app()
