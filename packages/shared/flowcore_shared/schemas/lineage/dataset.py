# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class DatasetType(str, Enum):
    DATABASE_TABLE = "DATABASE_TABLE"
    FILE = "FILE"
    API = "API"
    STREAM = "STREAM"
    QUEUE = "QUEUE"
    OBJECT_STORAGE = "OBJECT_STORAGE"
    WAREHOUSE = "WAREHOUSE"
    CUSTOM = "CUSTOM"

class DatasetBase(BaseModel):
    name: str = Field(..., description="Name of the dataset")
    type: DatasetType = Field(..., description="The type of the dataset")
    description: Optional[str] = Field(None, description="Business glossary description")
    owner: Optional[str] = Field(None, description="Owner of the dataset")

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[DatasetType] = None
    description: Optional[str] = None
    owner: Optional[str] = None

class DatasetVersion(BaseModel):
    id: str
    dataset_id: str
    schema_version: int
    schema_snapshot: Dict[str, Any]
    created_at: datetime

class Dataset(DatasetBase):
    id: str
    workspace_id: str
    environment_id: Optional[str] = None
    version: int = Field(default=1, description="Current schema version of the dataset")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
