from fastapi import APIRouter, Depends
from flowcore_server.services.dashboard import DashboardService
from flowcore_server.dependencies.core import get_uow
from flowcore_server.models.dashboard import DashboardResponse
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.auth import require_permissions, UserInDB

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardResponse)
async def get_dashboard(uow: AbstractUnitOfWork = Depends(get_uow), user: UserInDB = Depends(require_permissions([]))):
    """
    Get aggregated dashboard statistics.
    """
    service = DashboardService(uow)
    return await service.get_dashboard()
