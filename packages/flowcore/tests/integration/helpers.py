from typing import List, Tuple
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.pipeline.execution_step import ExecutionStep
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.dependencies.node import Node
from flowcore.models.dependencies.edge import Edge

def build_graph(nodes_def: List[str], edges_def: List[Tuple[str, str]]) -> Tuple[PipelineVersion, DependencyGraph]:
    steps = [ExecutionStep(step_id=n, connector_id="dummy", depends_on=[]) for n in nodes_def]
    # Update depends_on
    step_dict = {s.step_id: s for s in steps}
    for s, t in edges_def:
        step_dict[t].depends_on.append(s)
        
    pv = PipelineVersion(
        id="pv_test",
        pipeline_id="pipe_test",
        version="1.0.0",
        steps=steps
    )
    
    nodes = {s.step_id: Node(node_id=s.step_id) for s in steps}
    edges = [Edge(source=s, target=t) for s, t in edges_def]
    graph = DependencyGraph(nodes=nodes, edges=edges)
    return pv, graph
