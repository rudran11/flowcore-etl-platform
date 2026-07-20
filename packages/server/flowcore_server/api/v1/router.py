from fastapi import APIRouter
from .system import router as system_router
from .plugins import router as plugins_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(system_router)
api_router.include_router(plugins_router)
