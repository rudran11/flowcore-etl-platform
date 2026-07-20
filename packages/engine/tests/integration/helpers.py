from typing import List, Tuple
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.pipeline.execution_step import ExecutionStep
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph
from flowcore_shared.schemas.dependencies.node import Node
from flowcore_shared.schemas.dependencies.edge import Edge

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
