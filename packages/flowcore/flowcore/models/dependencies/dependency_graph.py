# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Dependency graph schema and topological resolution."""

from typing import Dict, List, Set
from pydantic import Field, model_validator
from flowcore_shared.schemas.base.models import FlowCoreBaseModel
from flowcore_shared.exceptions.validation import ValidationError
from .node import Node
from .edge import Edge

class DependencyGraph(FlowCoreBaseModel):
    """
    Represents a Directed Acyclic Graph (DAG) of execution dependencies.
    """
    nodes: Dict[str, Node] = Field(default_factory=dict, description="Map of node IDs to Node objects.")
    edges: List[Edge] = Field(default_factory=list, description="List of directed dependencies.")

    @model_validator(mode="after")
    def validate_graph(self) -> "DependencyGraph":
        """
        Ensures all edges reference valid nodes and the graph contains no cycles.
        """
        # 1. Validate edge references
        for edge in self.edges:
            if edge.source not in self.nodes:
                raise ValueError(f"Edge source '{edge.source}' does not exist in nodes.")
            if edge.target not in self.nodes:
                raise ValueError(f"Edge target '{edge.target}' does not exist in nodes.")
        
        # 2. Cycle detection via Kahn's algorithm (Topological Sort test)
        # Calculate in-degree for all nodes
        in_degree = {node_id: 0 for node_id in self.nodes}
        for edge in self.edges:
            in_degree[edge.target] += 1
            
        # Queue for nodes with 0 in-degree
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        visited_count = 0
        
        # Build adjacency list for fast traversal
        adj = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            adj[edge.source].append(edge.target)
            
        while queue:
            current = queue.pop(0)
            visited_count += 1
            for neighbor in adj[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if visited_count != len(self.nodes):
            raise ValueError("Dependency graph contains a cycle. Cyclic dependencies are not allowed.")
            
        return self

    def get_topological_sort(self) -> List[str]:
        """
        Returns a valid execution order of node IDs.
        """
        in_degree = {node_id: 0 for node_id in self.nodes}
        adj = {node_id: [] for node_id in self.nodes}
        
        for edge in self.edges:
            in_degree[edge.target] += 1
            adj[edge.source].append(edge.target)
            
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort queue to ensure deterministic execution order for nodes at the same depth
            queue.sort() 
            current = queue.pop(0)
            result.append(current)
            for neighbor in adj[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        return result
