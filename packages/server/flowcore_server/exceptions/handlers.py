import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from flowcore_engine.exceptions.plugin import PluginLoadError
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from .models import RFC7807Error

async def plugin_load_error_handler(request: Request, exc: PluginLoadError):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    err = RFC7807Error(
        type="about:blank",
        title="Plugin Load Error",
        status=500,
        flowcore_code="FLOWCORE-1001",
        detail=str(exc),
        instance=req_id
    )
    return JSONResponse(status_code=500, content=err.model_dump())

async def validation_error_handler(request: Request, exc: ValidationError | RequestValidationError):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    err = RFC7807Error(
        type="about:blank",
        title="Validation Error",
        status=422,
        flowcore_code="FLOWCORE-2001",
        detail=str(exc),
        instance=req_id
    )
    return JSONResponse(status_code=422, content=err.model_dump())

async def value_error_handler(request: Request, exc: ValueError):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    err = RFC7807Error(
        type="about:blank",
        title="Bad Request",
        status=400,
        flowcore_code="FLOWCORE-3001",
        detail=str(exc),
        instance=req_id
    )
    return JSONResponse(status_code=400, content=err.model_dump())

async def global_exception_handler(request: Request, exc: Exception):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    err = RFC7807Error(
        type="about:blank",
        title="Internal Server Error",
        status=500,
        flowcore_code="FLOWCORE-9999",
        detail="An unexpected error occurred.",
        instance=req_id
    )
    return JSONResponse(status_code=500, content=err.model_dump())
