# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Pipeline version metadata schema."""

from typing import List
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity
from .execution_step import ExecutionStep

class PipelineVersion(MetadataEntity):
    """
    Represents an immutable snapshot of a Pipeline's execution steps.
    """
    pipeline_id: str = Field(..., description="The parent Pipeline ID.")
    version: str = Field(..., description="Semantic version or git hash identifying this snapshot.")
    steps: List[ExecutionStep] = Field(
        default_factory=list, 
        description="The flat list of execution steps. Topology is resolved via depends_on fields."
    )
    dsl_definition: dict = Field(default_factory=dict, description="Raw YAML equivalent JSON dictionary.")
    graph_definition: dict = Field(default_factory=dict, description="Visual builder node/edge state.")
