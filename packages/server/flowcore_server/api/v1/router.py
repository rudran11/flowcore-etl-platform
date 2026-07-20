from fastapi import APIRouter
from .plugins import router as plugins_router
from .system import router as system_router
from .pipelines import router as pipelines_router
from .runs import router as runs_router
from .dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(system_router)
api_router.include_router(plugins_router)
api_router.include_router(pipelines_router)
api_router.include_router(runs_router)
api_router.include_router(dashboard_router)
