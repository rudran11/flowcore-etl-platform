from typing import Optional, List
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class Folder(MetadataEntity):
    name: str = Field(..., description="The name of the folder.")
    workspace_id: str = Field(..., description="The workspace this folder belongs to.")
    parent_id: Optional[str] = Field(None, description="The ID of the parent folder.")
    color: Optional[str] = Field(None, description="Color code for the folder.")

class Tag(MetadataEntity):
    name: str = Field(..., description="The name of the tag.")
    workspace_id: str = Field(..., description="The workspace this tag belongs to.")
    color: Optional[str] = Field(None, description="Color code for the tag.")
