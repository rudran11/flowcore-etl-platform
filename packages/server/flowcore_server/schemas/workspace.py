from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from flowcore.models.workspace import Folder, Tag

class FolderCreate(BaseModel):
    name: str = Field(..., description="The name of the folder.")
    parent_id: Optional[str] = Field(None, description="The ID of the parent folder.")
    color: Optional[str] = Field(None, description="Color code for the folder.")

class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The name of the folder.")
    parent_id: Optional[str] = Field(None, description="The ID of the parent folder.")
    color: Optional[str] = Field(None, description="Color code for the folder.")

class FolderResponse(BaseModel):
    folder: Folder = Field(..., description="The folder metadata.")
    pipeline_count: int = Field(0, description="Number of pipelines in this folder.")
    last_updated: Optional[str] = Field(None, description="Last update timestamp of any pipeline in this folder.")

class TagCreate(BaseModel):
    name: str = Field(..., description="The name of the tag.")
    color: Optional[str] = Field(None, description="Color code for the tag.")

class UserWorkspaceSettingsResponse(BaseModel):
    preferred_view: str = Field("grid", description="Preferred view (grid, list, compact).")
    default_sort: str = Field("updated_at", description="Default sort field.")
    sidebar_collapsed: bool = Field(False, description="Whether sidebar is collapsed.")
    expanded_folders: List[str] = Field(default_factory=list, description="List of expanded folder IDs.")

class UserWorkspaceSettingsUpdate(BaseModel):
    preferred_view: Optional[str] = Field(None)
    default_sort: Optional[str] = Field(None)
    sidebar_collapsed: Optional[bool] = Field(None)
    expanded_folders: Optional[List[str]] = Field(None)
