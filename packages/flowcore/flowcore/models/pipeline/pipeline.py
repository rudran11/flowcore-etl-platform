# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Pipeline metadata schema."""

from typing import List, Optional
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity


class Pipeline(MetadataEntity):
    """
    Represents the logical parent container of an ETL workflow.
    Does not contain the execution DAG (that belongs to PipelineVersion).
    """
    name: str = Field(..., description="The human-readable name of the pipeline.")
    workspace_id: str = Field(..., description="The workspace this pipeline belongs to")
    owner: str = Field(..., description="The team or individual owning this pipeline.")
    description: Optional[str] = Field(None, description="Detailed description of what this pipeline accomplishes.")
    tags: List[str] = Field(default_factory=list, description="Categorization tags for searching and filtering.")
    folder_id: Optional[str] = Field(None, description="The ID of the folder containing this pipeline.")
    is_archived: bool = Field(False, description="Whether the pipeline is archived.")
    is_favorite: Optional[bool] = Field(None, description="Whether the pipeline is favorited by the current user.")
    icon: Optional[str] = Field(None, description="Icon identifier for UI.")
    color: Optional[str] = Field(None, description="Color code (hex) for UI.")
