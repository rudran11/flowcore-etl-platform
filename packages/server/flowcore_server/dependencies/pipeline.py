from fastapi import Depends
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.core import get_uow
from flowcore_server.services.pipeline import PipelineService

def get_pipeline_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> PipelineService:
    """Dependency that provides the PipelineService instance."""
    return PipelineService(uow)
