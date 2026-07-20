from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from flowcore_engine.exceptions.plugin import PluginLoadError
from .config import settings
from .api.v1.router import api_router
from .exceptions.handlers import (
    plugin_load_error_handler,
    validation_error_handler,
    value_error_handler,
    global_exception_handler
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="FlowCore Execution API",
        version="1.0.0",
        description="REST API gateway and control plane for FlowCore."
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(PluginLoadError, plugin_load_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Routers
    app.include_router(api_router)

    return app

app = create_app()
