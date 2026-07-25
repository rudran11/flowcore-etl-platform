# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from .dataset import Dataset

class ConfidenceLevel(str, Enum):
    DETECTED = "DETECTED"
    DECLARED = "DECLARED"
    MANUAL = "MANUAL"

class LineageNode(BaseModel):
    id: str
    type: str = Field(..., description="Type of the node (DATASET, PIPELINE, EXECUTION, etc.)")
    name: str
    data: Any = Field(None, description="Additional context data")

class LineageEdgeBase(BaseModel):
    upstream_id: str = Field(..., description="The ID of the source dataset/node")
    downstream_id: str = Field(..., description="The ID of the target dataset/node")
    pipeline_id: Optional[str] = Field(None, description="The pipeline that created this edge")
    execution_id: Optional[str] = Field(None, description="The specific execution that created this edge")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.DETECTED)

class LineageEdgeCreate(LineageEdgeBase):
    pass

class LineageEdge(LineageEdgeBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LineageGraph(BaseModel):
    nodes: List[LineageNode]
    edges: List[LineageEdge]
