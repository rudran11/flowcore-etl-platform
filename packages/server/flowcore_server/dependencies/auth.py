from typing import List, Callable
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from flowcore_server.services.auth import AuthService
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.core import get_uow
from flowcore_shared.schemas.auth import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    uow: AbstractUnitOfWork = Depends(get_uow)
) -> UserInDB:
    try:
        payload = AuthService.verify_token(token, token_type="access")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    async with uow:
        user = await uow.users.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

def require_permissions(required_permissions: List[str]) -> Callable:
    async def permission_checker(
        x_workspace_id: str = Header(..., description="The ID of the workspace"),
        user: UserInDB = Depends(get_current_user),
        uow: AbstractUnitOfWork = Depends(get_uow)
    ):
        async with uow:
            member = await uow.workspace_members.get_member(user.id, x_workspace_id)
            if not member:
                raise HTTPException(status_code=403, detail="Not a member of this workspace")
            
            role = await uow.roles.get(member.role_id)
            if not role:
                raise HTTPException(status_code=403, detail="Role not found")
            
            user_perms = set()
            for p in role.permissions:
                if p.name == "Admin All":
                    user_perms.add("admin:*")
                else:
                    user_perms.add(p.name.lower().replace(" ", ":"))
                    
            if "admin:*" in user_perms:
                return user
                
            for req_perm in required_permissions:
                if req_perm not in user_perms:
                    raise HTTPException(status_code=403, detail=f"Missing permission: {req_perm}")
                    
            return user
    return permission_checker
