from typing import List, Callable, Optional
import hashlib
import hmac
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from flowcore_server.services.auth import AuthService
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.core import get_uow
from flowcore_shared.schemas.auth import UserInDB, Principal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

async def get_current_principal(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    uow: AbstractUnitOfWork = Depends(get_uow)
) -> Principal:
    # Manual token extraction if OAuth2PasswordBearer didn't get it (or we can just use the token if present)
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    scheme, param = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
    actual_token = param

    # Check if API Key
    if actual_token.startswith("fc_"):
        key_hash = hashlib.sha256(actual_token.encode()).hexdigest()
        async with uow:
            db_key = await uow.api_keys.get_by_hash(key_hash)
            if not db_key:
                raise HTTPException(status_code=401, detail="Invalid API Key")
            
            # Constant time compare just in case, though get_by_hash already checks equality
            if not hmac.compare_digest(db_key.key_hash, key_hash):
                raise HTTPException(status_code=401, detail="Invalid API Key")
                
            await uow.api_keys.record_usage(str(db_key.id))
            await uow.commit()

            return Principal(
                is_api_key=True,
                identity_id=str(db_key.id),
                name=db_key.name,
                workspace_id=str(db_key.workspace_id),
                scopes=db_key.scopes,
                user=None
            )

    # Otherwise, process as JWT
    try:
        payload = AuthService.verify_token(actual_token, token_type="access")
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
        
        return Principal(
            is_api_key=False,
            identity_id=user.id,
            name=user.username,
            workspace_id=None,
            scopes=[],
            user=user
        )

async def get_current_user(
    principal: Principal = Depends(get_current_principal)
) -> UserInDB:
    if principal.is_api_key or not principal.user:
        raise HTTPException(status_code=403, detail="API Keys cannot be used for this endpoint")
    return principal.user

def require_permissions(required_permissions: List[str]) -> Callable:
    async def permission_checker(
        x_workspace_id: str = Header(..., description="The ID of the workspace"),
        principal: Principal = Depends(get_current_principal),
        uow: AbstractUnitOfWork = Depends(get_uow)
    ) -> Principal:
        if principal.is_api_key:
            if principal.workspace_id != x_workspace_id:
                raise HTTPException(status_code=403, detail="API Key does not belong to this workspace")
                
            for req_perm in required_permissions:
                if req_perm not in principal.scopes and "admin:*" not in principal.scopes:
                    raise HTTPException(status_code=403, detail=f"API Key missing scope: {req_perm}")
                    
            return principal

        # Normal User logic
        user = principal.user
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
                # Still add it to the principal scopes for downstream code
                principal.scopes = ["admin:*"] + list(user_perms)
                return principal
                
            for req_perm in required_permissions:
                if req_perm not in user_perms:
                    raise HTTPException(status_code=403, detail=f"Missing permission: {req_perm}")
            
            principal.scopes = list(user_perms)
            return principal
            
    return permission_checker
