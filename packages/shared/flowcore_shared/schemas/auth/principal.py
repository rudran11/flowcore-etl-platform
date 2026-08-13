from typing import Optional, List
from pydantic import BaseModel
from .user import UserInDB

class Principal(BaseModel):
    is_api_key: bool
    identity_id: str
    name: str
    workspace_id: Optional[str] = None
    scopes: List[str] = []
    user: Optional[UserInDB] = None
