from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List, Optional
from flowcore_shared.schemas.lineage.dataset import Dataset, DatasetCreate, DatasetUpdate
from flowcore_server.dependencies.lineage import get_lineage_service
from flowcore_server.dependencies.auth import get_current_user, require_permissions
from flowcore_server.services.lineage_service import LineageService
from flowcore_shared.schemas.auth.user import UserInDB

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("", response_model=Dataset, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    data: DatasetCreate,
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    user: UserInDB = Depends(require_permissions(["dataset:create"]))
):
    return await service.create_dataset(x_workspace_id, data)

@router.get("", response_model=List[Dataset])
async def list_datasets(
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    user: UserInDB = Depends(require_permissions(["dataset:read"]))
):
    return await service.list_datasets(x_workspace_id)

@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str,
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    user: UserInDB = Depends(require_permissions(["dataset:read"]))
):
    dataset = await service.get_dataset(dataset_id)
    if not dataset or dataset.workspace_id != x_workspace_id:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.put("/{dataset_id}", response_model=Dataset)
async def update_dataset(
    dataset_id: str,
    data: DatasetUpdate,
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    user: UserInDB = Depends(require_permissions(["dataset:edit"]))
):
    return await service.update_dataset(dataset_id, data)

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    user: UserInDB = Depends(require_permissions(["dataset:delete"]))
):
    await service.delete_dataset(dataset_id)
