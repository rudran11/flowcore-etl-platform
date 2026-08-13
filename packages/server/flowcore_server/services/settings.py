import uuid
import secrets
import hashlib
from typing import List, Optional
from fastapi import HTTPException
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_shared.schemas.auth import Workspace, WorkspaceMember, Role, ApiKeyResponse, ApiKeyCreate, ApiKeyCreateResponse

class SettingsService:
    @staticmethod
    async def get_workspace(uow: AbstractUnitOfWork, workspace_id: str) -> Workspace:
        async with uow:
            workspace = await uow.workspaces.get(workspace_id)
            if not workspace:
                raise HTTPException(status_code=404, detail="Workspace not found")
            return workspace

    @staticmethod
    async def get_roles(uow: AbstractUnitOfWork, org_id: str) -> List[Role]:
        async with uow:
            return await uow.roles.list_by_organization(org_id)

    @staticmethod
    async def list_members(uow: AbstractUnitOfWork, workspace_id: str) -> List[dict]:
        async with uow:
            members = await uow.workspace_members.list_by_workspace(workspace_id)
            results = []
            for m in members:
                user = await uow.users.get(m.user_id)
                role = await uow.roles.get(m.role_id)
                results.append({
                    "user_id": m.user_id,
                    "email": user.email if user else "Unknown",
                    "full_name": user.full_name if user else "Unknown",
                    "role_id": m.role_id,
                    "role_name": role.name if role else "Unknown",
                    "joined_at": m.created_at
                })
            return results

    @staticmethod
    async def update_member_role(uow: AbstractUnitOfWork, workspace_id: str, user_id: str, new_role_id: str, principal_user_id: str) -> dict:
        async with uow:
            member = await uow.workspace_members.get_member(user_id, workspace_id)
            if not member:
                raise HTTPException(status_code=404, detail="Member not found")
            
            # Check last admin if they are an admin and their role is changing
            old_role = await uow.roles.get(member.role_id)
            if old_role and old_role.name == "Workspace Admin":
                # they are an admin. Is this the last admin?
                members = await uow.workspace_members.list_by_workspace(workspace_id)
                admin_count = 0
                for m in members:
                    r = await uow.roles.get(m.role_id)
                    if r and r.name == "Workspace Admin":
                        admin_count += 1
                
                if admin_count <= 1:
                    raise HTTPException(status_code=400, detail="Cannot change role of the last Workspace Admin")
            
            updated_member = await uow.workspace_members.update_role(user_id, workspace_id, new_role_id)
            await uow.audit_logs.create(
                entity_id=workspace_id,
                entity_type="workspace",
                action="update_member_role",
                details={"user_id": user_id, "new_role_id": new_role_id, "performed_by": principal_user_id}
            )
            await uow.commit()
            return {"success": True}

    @staticmethod
    async def remove_member(uow: AbstractUnitOfWork, workspace_id: str, user_id: str, principal_user_id: str) -> dict:
        async with uow:
            member = await uow.workspace_members.get_member(user_id, workspace_id)
            if not member:
                raise HTTPException(status_code=404, detail="Member not found")
            
            old_role = await uow.roles.get(member.role_id)
            if old_role and old_role.name == "Workspace Admin":
                members = await uow.workspace_members.list_by_workspace(workspace_id)
                admin_count = 0
                for m in members:
                    r = await uow.roles.get(m.role_id)
                    if r and r.name == "Workspace Admin":
                        admin_count += 1
                
                if admin_count <= 1:
                    raise HTTPException(status_code=400, detail="Cannot remove the last Workspace Admin")
            
            await uow.workspace_members.remove_member(user_id, workspace_id)
            await uow.audit_logs.create(
                entity_id=workspace_id,
                entity_type="workspace",
                action="remove_member",
                details={"user_id": user_id, "performed_by": principal_user_id}
            )
            await uow.commit()
            return {"success": True}

    @staticmethod
    async def create_api_key(uow: AbstractUnitOfWork, workspace_id: str, request: ApiKeyCreate, principal_user_id: str) -> ApiKeyCreateResponse:
        # Generate 32 bytes raw key -> 64 hex chars
        raw_key = secrets.token_hex(32)
        full_key = f"fc_{raw_key}"
        
        # prefix is first 8 chars of raw key + ...
        prefix = f"fc_{raw_key[:8]}..."
        
        # hash it
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        async with uow:
            db_key = await uow.api_keys.create(
                workspace_id=workspace_id,
                name=request.name,
                key_hash=key_hash,
                prefix=prefix,
                scopes=request.scopes,
                created_by=principal_user_id
            )
            await uow.audit_logs.create(
                entity_id=workspace_id,
                entity_type="workspace",
                action="create_api_key",
                details={"key_name": request.name, "performed_by": principal_user_id}
            )
            await uow.commit()
            
            return ApiKeyCreateResponse(
                id=str(db_key.id),
                workspace_id=str(db_key.workspace_id),
                name=db_key.name,
                prefix=db_key.prefix,
                scopes=db_key.scopes,
                expires_at=db_key.expires_at,
                last_used_at=db_key.last_used_at,
                revoked_at=db_key.revoked_at,
                created_at=db_key.created_at,
                key=full_key
            )

    @staticmethod
    async def list_api_keys(uow: AbstractUnitOfWork, workspace_id: str) -> List[ApiKeyResponse]:
        async with uow:
            keys = await uow.api_keys.list_by_workspace(workspace_id)
            return [
                ApiKeyResponse(
                    id=str(k.id),
                    workspace_id=str(k.workspace_id),
                    name=k.name,
                    prefix=k.prefix,
                    scopes=k.scopes,
                    expires_at=k.expires_at,
                    last_used_at=k.last_used_at,
                    revoked_at=k.revoked_at,
                    created_at=k.created_at
                )
                for k in keys if k.revoked_at is None
            ]

    @staticmethod
    async def revoke_api_key(uow: AbstractUnitOfWork, workspace_id: str, key_id: str, principal_user_id: str) -> dict:
        async with uow:
            success = await uow.api_keys.delete(key_id, workspace_id)
            if not success:
                raise HTTPException(status_code=404, detail="API Key not found or already revoked")
            
            await uow.audit_logs.create(
                entity_id=workspace_id,
                entity_type="workspace",
                action="revoke_api_key",
                details={"key_id": key_id, "performed_by": principal_user_id}
            )
            await uow.commit()
            return {"success": True}
