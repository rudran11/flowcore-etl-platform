# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Execution step metadata schema."""

from typing import List, Dict, Any
from pydantic import Field
from flowcore_shared.schemas.base.models import FlowCoreBaseModel

class ExecutionStep(FlowCoreBaseModel):
    """
    Represents a single executable node within a PipelineVersion's DAG.
    """
    step_id: str = Field(..., description="The unique identifier for this step within the pipeline.")
    connector_id: str = Field(..., description="The ID of the connector to execute for this step.")
    depends_on: List[str] = Field(
        default_factory=list, 
        description="A list of step_ids that must successfully complete before this step runs."
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Step-specific execution parameters provided to the connector at runtime."
    )
