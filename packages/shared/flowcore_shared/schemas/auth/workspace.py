from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: str

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Workspace(WorkspaceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
