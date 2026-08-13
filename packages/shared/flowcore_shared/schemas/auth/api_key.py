from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class ApiKeyCreate(BaseModel):
    name: str = Field(..., description="Name of the API key")
    scopes: List[str] = Field(default=[], description="List of permission scopes")

class ApiKeyResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    prefix: str
    scopes: List[str]
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    revoked_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApiKeyCreateResponse(ApiKeyResponse):
    key: str = Field(..., description="The plaintext API key. Displayed only once.")
