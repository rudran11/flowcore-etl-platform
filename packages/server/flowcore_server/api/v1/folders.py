from fastapi import APIRouter, Depends, status
from typing import List
from flowcore_server.dependencies.core import get_uow
from flowcore_server.dependencies.auth import get_current_user, UserInDB
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.services.folder import FolderService
from flowcore_server.schemas.workspace import FolderCreate, FolderUpdate, FolderResponse
from flowcore.models.workspace import Folder

router = APIRouter(prefix="/folders", tags=["Folders"])

def get_folder_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> FolderService:
    return FolderService(uow)

@router.get("", response_model=List[FolderResponse])
async def list_folders(
    service: FolderService = Depends(get_folder_service),
    user: UserInDB = Depends(get_current_user)
):
    return await service.list_folders()

@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: str,
    service: FolderService = Depends(get_folder_service),
    user: UserInDB = Depends(get_current_user)
):
    return await service.get_folder(folder_id)

@router.post("", response_model=Folder, status_code=status.HTTP_201_CREATED)
async def create_folder(
    request: FolderCreate,
    service: FolderService = Depends(get_folder_service),
    user: UserInDB = Depends(get_current_user)
):
    return await service.create_folder(request)

@router.put("/{folder_id}", response_model=Folder)
async def update_folder(
    folder_id: str,
    request: FolderUpdate,
    service: FolderService = Depends(get_folder_service),
    user: UserInDB = Depends(get_current_user)
):
    return await service.update_folder(folder_id, request)

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: str,
    service: FolderService = Depends(get_folder_service),
    user: UserInDB = Depends(get_current_user)
):
    await service.delete_folder(folder_id)
