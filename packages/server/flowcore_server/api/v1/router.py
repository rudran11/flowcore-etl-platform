from fastapi import APIRouter
from .plugins import router as plugins_router
from .system import router as system_router
from .pipelines import router as pipelines_router
from .runs import router as runs_router
from .dashboard import router as dashboard_router
from .schedules import router as schedules_router
from .auth import router as auth_router
from .workspaces import router as workspaces_router
from .environments import router as environments_router
from .datasets import router as datasets_router
from .lineage import router as lineage_router
from .folders import router as folders_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(system_router)
api_router.include_router(plugins_router)
api_router.include_router(pipelines_router)
api_router.include_router(runs_router)
api_router.include_router(dashboard_router)
api_router.include_router(schedules_router)
api_router.include_router(environments_router)
api_router.include_router(datasets_router)
api_router.include_router(lineage_router)
api_router.include_router(folders_router)
