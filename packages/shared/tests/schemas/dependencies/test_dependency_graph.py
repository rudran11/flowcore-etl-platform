import pytest
from pydantic import ValidationError
from flowcore.models.dependencies.node import Node
from flowcore.models.dependencies.edge import Edge
from flowcore.models.dependencies.dependency_graph import DependencyGraph

def test_dependency_graph_valid():
    graph = DependencyGraph(
        nodes={
            "A": Node(node_id="A"),
            "B": Node(node_id="B"),
            "C": Node(node_id="C")
        },
        edges=[
            Edge(source="A", target="B"),
            Edge(source="B", target="C")
        ]
    )
    order = graph.get_topological_sort()
    assert order == ["A", "B", "C"]

def test_dependency_graph_cycle():
    with pytest.raises(ValidationError, match="contains a cycle"):
        DependencyGraph(
            nodes={
                "A": Node(node_id="A"),
                "B": Node(node_id="B")
            },
            edges=[
                Edge(source="A", target="B"),
                Edge(source="B", target="A")
            ]
        )

def test_dependency_graph_invalid_edge():
    with pytest.raises(ValidationError, match="does not exist in nodes"):
        DependencyGraph(
            nodes={
                "A": Node(node_id="A")
            },
            edges=[
                Edge(source="A", target="B")
            ]
        )

def test_dependency_graph_deterministic_sort():
    graph = DependencyGraph(
        nodes={
            "A": Node(node_id="A"),
            "C": Node(node_id="C"),
            "B": Node(node_id="B")
        },
        edges=[
            Edge(source="A", target="B"),
            Edge(source="A", target="C")
        ]
    )
    # Both B and C depend on A, but have no dependencies on each other.
    # Deterministic sort should alphabetize them at the same depth.
    order = graph.get_topological_sort()
    assert order == ["A", "B", "C"]
