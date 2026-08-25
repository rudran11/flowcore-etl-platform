from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: str
    max_concurrent_runs: int = 10

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_concurrent_runs: Optional[int] = None

class Workspace(WorkspaceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
