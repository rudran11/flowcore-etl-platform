import yaml
from pathlib import Path
from flowcore.parsing.parser import DSLParser
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.dependencies.node import Node
from flowcore.models.dependencies.edge import Edge
from flowcore.models.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore.engine.plugins.manager import PluginManager
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.executor.thread import ThreadExecutor
from flowcore.engine.runner.engine import EngineRunner
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

    def run(self, pipeline_path: str = None, pipeline_version: PipelineVersion = None):
        print("Loading pipeline...")
        if pipeline_version:
            pv = pipeline_version
        elif pipeline_path:
            pv = self.validate(pipeline_path)
        else:
            raise ValueError("Must provide pipeline_path or pipeline_version")
        
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
        result = runner.run()
        duration = time.time() - start
        print(f"\nFinished\nDuration: {duration:.2f} seconds")
        return result

    def compile(self, pipeline_path: str):
        pass

    def list_plugins(self):
        return self.plugin_manager.get_all_plugins()


class PipelineBuilder:
    """Fluent API for programmatic pipeline generation."""
    def __init__(self, name: str):
        self.name = name
        self.steps = []
        self._last_step_id = None
        self._step_counter = 0

    def source(self, plugin_id: str, **kwargs) -> 'PipelineBuilder':
        step_id = f"source_{self._step_counter}"
        self._step_counter += 1
        
        # Sources typically have no depends_on in a linear flow
        self.steps.append({
            "step_id": step_id,
            "connector_id": plugin_id,
            "depends_on": [],
            "parameters": kwargs
        })
        self._last_step_id = step_id
        return self

    def transform(self, plugin_id: str, **kwargs) -> 'PipelineBuilder':
        step_id = f"transform_{self._step_counter}"
        self._step_counter += 1
        
        # Ensure 'transform-' prefix is handled implicitly or explicitly
        actual_plugin = plugin_id if plugin_id.startswith("transform-") else f"transform-{plugin_id}"
        
        depends_on = [self._last_step_id] if self._last_step_id else []
        self.steps.append({
            "step_id": step_id,
            "connector_id": actual_plugin,
            "depends_on": depends_on,
            "parameters": kwargs
        })
        self._last_step_id = step_id
        return self

    def destination(self, plugin_id: str, **kwargs) -> 'PipelineBuilder':
        step_id = f"destination_{self._step_counter}"
        self._step_counter += 1
        
        depends_on = [self._last_step_id] if self._last_step_id else []
        self.steps.append({
            "step_id": step_id,
            "connector_id": plugin_id,
            "depends_on": depends_on,
            "parameters": kwargs
        })
        self._last_step_id = step_id
        return self

    def compile(self) -> dict:
        """Returns the canonical dictionary representing the pipeline DSL."""
        return {
            "version": "1.0",
            "pipeline": {
                "name": self.name,
                "owner": "sdk_user"
            },
            "steps": self.steps
        }

    def run(self, flowcore_client: FlowCore = None):
        """Compiles and executes the pipeline."""
        if not flowcore_client:
            flowcore_client = FlowCore()
        
        from flowcore.parsing.parser import DSLParser
        pipeline, steps = DSLParser.parse_pipeline_dsl(self.compile())
        
        pv = PipelineVersion(
            id=str(uuid.uuid4()),
            pipeline_id=pipeline.id,
            version="local",
            steps=steps
        )
        return flowcore_client.run(pipeline_version=pv)
