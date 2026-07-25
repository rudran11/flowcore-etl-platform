# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from .dataset import Dataset
from flowcore_shared.schemas.pipeline.pipeline import Pipeline
from flowcore_shared.schemas.operational.schedule import Schedule

class ImpactEntity(BaseModel):
    id: str
    type: str = Field(..., description="E.g. PIPELINE, DATASET, DASHBOARD")
    name: str
    depth: int = Field(..., description="How many hops away from the source")

class ImpactReport(BaseModel):
    source_dataset_id: str
    affected_pipelines: List[ImpactEntity]
    affected_datasets: List[ImpactEntity]
    affected_schedules: List[ImpactEntity]
    risk_score: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    criticality: int = Field(default=0, description="Score based on downstream usage")

class DependencyReport(BaseModel):
    target_dataset_id: str
    upstream_datasets: List[ImpactEntity]
    upstream_pipelines: List[ImpactEntity]
