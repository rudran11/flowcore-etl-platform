# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Graph edge schema."""

from pydantic import Field
from flowcore_shared.schemas.base.models import FlowCoreBaseModel

class Edge(FlowCoreBaseModel):
    """
    Represents a directed dependency relationship from a source node to a target node.
    Source must complete before Target can begin.
    """
    source: str = Field(..., description="The ID of the node that must complete first.")
    target: str = Field(..., description="The ID of the node that depends on the source.")
