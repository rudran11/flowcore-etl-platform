from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PermissionBase(BaseModel):
    name: str
    description: str

class Permission(PermissionBase):
    id: str
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: Optional[str] = None # System roles have null org_id

class RoleCreate(RoleBase):
    permission_ids: List[str]

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None

class Role(RoleBase):
    id: str
    permissions: List[Permission] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkspaceMemberBase(BaseModel):
    user_id: str
    workspace_id: str
    role_id: str

class WorkspaceMemberCreate(WorkspaceMemberBase):
    pass

class WorkspaceMember(WorkspaceMemberBase):
    created_at: datetime
    
    class Config:
        from_attributes = True
