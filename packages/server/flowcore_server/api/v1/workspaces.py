from fastapi import APIRouter, Depends, HTTPException
from typing import List
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.core import get_uow
from flowcore_server.dependencies.auth import get_current_user
from flowcore_shared.schemas.auth import Workspace, UserInDB

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.get("/", response_model=List[Workspace])
async def list_user_workspaces(
    user: UserInDB = Depends(get_current_user),
    uow: AbstractUnitOfWork = Depends(get_uow)
):
    """
    List all workspaces the current user has access to.
    """
    async with uow:
        memberships = await uow.workspace_members.list_by_user(user.id)
        workspace_ids = [m.workspace_id for m in memberships]
        
        workspaces = []
        for wid in workspace_ids:
            ws = await uow.workspaces.get(wid)
            if ws:
                workspaces.append(ws)
                
        return workspaces
