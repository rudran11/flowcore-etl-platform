import yaml
from pathlib import Path
from flowcore_shared.parsing.parser import DSLParser
from flowcore_shared.schemas.pipeline.pipeline_version import PipelineVersion
from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph
from flowcore_shared.schemas.dependencies.node import Node
from flowcore_shared.schemas.dependencies.edge import Edge
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_engine.plugins.manager import PluginManager
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.executor.thread import ThreadExecutor
from flowcore_engine.runner.engine import EngineRunner
import uuid

class FlowCore:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins([plugin_dir])

    def load_pipeline(self, pipeline_path: str):
        path = Path(pipeline_path)
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {pipeline_path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        if "pipeline" in data and isinstance(data["pipeline"], dict):
            if "workspace_id" not in data["pipeline"]:
                data["pipeline"]["workspace_id"] = str(uuid.uuid4())
            
        pipeline, steps = DSLParser.parse_pipeline_dsl(data)
        
        # Synthesize a PipelineVersion for execution
        pipeline_version = PipelineVersion(
            id=str(uuid.uuid4()),
            pipeline_id=pipeline.id,
            version="local",
            steps=steps
        )
        return pipeline_version

    def validate(self, pipeline_path: str):
        print(f"Validating {pipeline_path}...")
        pv = self.load_pipeline(pipeline_path)
        # Check plugins
        missing = []
        for step in pv.steps:
            if not self.plugin_manager.get_plugin(step.connector_id):
                missing.append(step.connector_id)
        if missing:
            raise ValueError(f"Missing plugins: {missing}")
        print("[OK] Pipeline validated successfully.")
        return pv

    def run(self, pipeline_path: str):
        print("Loading pipeline...")
        pv = self.validate(pipeline_path)
        
        # Build dependency graph
        graph = DependencyGraph(nodes={}, edges=[])
        for step in pv.steps:
            graph.nodes[step.step_id] = Node(node_id=step.step_id)
            for dep in step.depends_on:
                graph.edges.append(Edge(source=dep, target=step.step_id))
                
        coordinator = ExecutionCoordinator(pipeline=pv, graph=graph)
        
        run_id = str(uuid.uuid4())
        run = ExecutionRun(
            id=run_id,
            workspace_id=str(uuid.uuid4()),
            pipeline_id=pv.pipeline_id,
            pipeline_version_id=pv.id,
            status=ExecutionState.PENDING,
            trigger_type="MANUAL"
        )
        coordinator.initialize_run(run)
        
        executor = ThreadExecutor(max_workers=5)
        runner = EngineRunner(coordinator, self.plugin_manager, executor)
        
        print("[OK] Executing DAG\n")
        import time
        start = time.time()
        runner.run()
        duration = time.time() - start
        print(f"\nFinished\nDuration: {duration:.2f} seconds")

    def compile(self, pipeline_path: str):
        pass

    def list_plugins(self):
        return self.plugin_manager.get_all_plugins()

