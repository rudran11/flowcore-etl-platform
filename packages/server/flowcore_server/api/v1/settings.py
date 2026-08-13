from typing import List
from fastapi import APIRouter, Depends, Header, status
from pydantic import BaseModel
from flowcore_server.services.settings import SettingsService
from flowcore_server.dependencies.settings import get_settings_service
from flowcore_server.dependencies.core import get_uow
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.auth import require_permissions
from flowcore_shared.schemas.auth import Workspace, Role, ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse, Principal

router = APIRouter(prefix="/settings", tags=["Settings"])

# Workspace Settings
class WorkspaceUpdateParams(BaseModel):
    name: str
    description: str

@router.get("/workspace", response_model=Workspace)
async def get_workspace_settings(
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["workspace:view"]))
):
    return await service.get_workspace(uow, x_workspace_id)

@router.put("/workspace", response_model=Workspace)
async def update_workspace_settings(
    params: WorkspaceUpdateParams,
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["workspace:update"]))
):
    async with uow:
        workspace = await uow.workspaces.get(x_workspace_id)
        if not workspace:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Workspace not found")
            
        workspace.name = params.name
        workspace.description = params.description
        await uow.commit()
        return workspace

# Roles
@router.get("/roles", response_model=List[Role])
async def list_roles(
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["workspace:view"]))
):
    workspace = await service.get_workspace(uow, x_workspace_id)
    return await service.get_roles(uow, workspace.organization_id)

# Members
@router.get("/members")
async def list_members(
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["member:view"]))
):
    return await service.list_members(uow, x_workspace_id)

class UpdateMemberRoleRequest(BaseModel):
    role_id: str

@router.patch("/members/{user_id}", status_code=status.HTTP_200_OK)
async def update_member_role(
    user_id: str,
    request: UpdateMemberRoleRequest,
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["member:update"]))
):
    return await service.update_member_role(uow, x_workspace_id, user_id, request.role_id, principal.identity_id)

@router.delete("/members/{user_id}", status_code=status.HTTP_200_OK)
async def remove_member(
    user_id: str,
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["member:delete"]))
):
    return await service.remove_member(uow, x_workspace_id, user_id, principal.identity_id)

# API Keys
@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["apikey:view"]))
):
    return await service.list_api_keys(uow, x_workspace_id)

@router.post("/api-keys", response_model=ApiKeyCreateResponse)
async def create_api_key(
    request: ApiKeyCreate,
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["apikey:create"]))
):
    return await service.create_api_key(uow, x_workspace_id, request, principal.identity_id)

@router.delete("/api-keys/{key_id}", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    key_id: str,
    x_workspace_id: str = Header(..., description="The ID of the workspace"),
    service: SettingsService = Depends(get_settings_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    principal: Principal = Depends(require_permissions(["apikey:delete"]))
):
    return await service.revoke_api_key(uow, x_workspace_id, key_id, principal.identity_id)
