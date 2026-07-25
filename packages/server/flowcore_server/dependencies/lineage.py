from fastapi import Depends
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.services.lineage_service import LineageService
from flowcore_server.dependencies.core import get_uow

def get_lineage_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> LineageService:
    return LineageService(uow)
