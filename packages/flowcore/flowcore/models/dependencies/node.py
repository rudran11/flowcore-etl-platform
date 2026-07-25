# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Graph node schema."""

from pydantic import Field
from flowcore_shared.schemas.base.models import FlowCoreBaseModel

class Node(FlowCoreBaseModel):
    """
    Represents a discrete node within a Dependency Graph.
    """
    node_id: str = Field(..., description="Unique identifier for the node.")
