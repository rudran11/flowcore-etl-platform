# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional
from pydantic import BaseModel, Field

class DatasetColumnBase(BaseModel):
    name: str = Field(..., description="Name of the column")
    data_type: str = Field(..., description="Data type (e.g. VARCHAR, INT)")
    description: Optional[str] = Field(None, description="Column description")
    is_nullable: bool = Field(default=True, description="Whether the column is nullable")
    is_primary_key: bool = Field(default=False, description="Whether the column is part of the primary key")

class DatasetColumnCreate(DatasetColumnBase):
    pass

class DatasetColumnUpdate(BaseModel):
    name: Optional[str] = None
    data_type: Optional[str] = None
    description: Optional[str] = None
    is_nullable: Optional[bool] = None
    is_primary_key: Optional[bool] = None

class DatasetColumn(DatasetColumnBase):
    id: str
    dataset_id: str
    dataset_version_id: Optional[str] = None

    class Config:
        from_attributes = True
