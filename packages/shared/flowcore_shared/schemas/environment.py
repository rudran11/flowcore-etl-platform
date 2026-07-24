# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Environment domain schema."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum
from flowcore_shared.schemas.base.models import MetadataEntity

class EnvironmentType(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    QA = "QA"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    CUSTOM = "CUSTOM"

class EnvironmentVariable(BaseModel):
    id: str = Field(..., description="Unique ID for this variable.")
    key: str = Field(..., description="The configuration key (e.g., DB_HOST).")
    value: str = Field(..., description="The value. If is_secret is True, this is returned as masked in APIs.")
    is_secret: bool = Field(default=False, description="Whether this variable is securely encrypted.")
    
class EnvironmentVariableCreate(BaseModel):
    key: str
    value: str
    is_secret: bool = False

class EnvironmentVariableUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    is_secret: Optional[bool] = None

class EnvironmentCreate(BaseModel):
    name: str = Field(..., description="Name of the environment.")
    description: Optional[str] = Field(None, description="Optional description.")
    type: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT)

class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[EnvironmentType] = None

class Environment(MetadataEntity):
    """
    Represents an isolated configuration environment (e.g. Production, Staging).
    """
    workspace_id: str = Field(..., description="The workspace this environment belongs to.")
    name: str = Field(..., description="Name of the environment.")
    description: Optional[str] = Field(None, description="Optional description.")
    type: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT)
    variables: List[EnvironmentVariable] = Field(default_factory=list, description="Variables configured for this environment.")
    
class PipelineEnvironmentBinding(BaseModel):
    pipeline_id: str
    environment_id: str

class EnvironmentOverride(BaseModel):
    """
    Passed dynamically during pipeline execution to override bound environment variables.
    """
    key: str
    value: str
