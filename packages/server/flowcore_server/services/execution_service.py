from typing import Any, Dict
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.application.registry import AbstractRunRegistry
from flowcore_server.application.pipeline_repo import AbstractPipelineRepository
from flowcore_server.application.cancellation import CancellationStrategy
from flowcore_server.application.background import BackgroundExecutionStrategy
from flowcore_server.application.engine_factory import ExecutionEngineFactory
from flowcore_engine.plugins.manager import PluginManager

class ExecutionService:
    """
    Core service wrapping engine execution and lifecycle management.
    Isolates the engine layer from HTTP routers.
    """
    def __init__(
        self,
        pipeline_repo: AbstractPipelineRepository,
        engine_factory: ExecutionEngineFactory,
        run_registry: AbstractRunRegistry,
        cancellation_strategy: CancellationStrategy,
        background_strategy: BackgroundExecutionStrategy,
        plugin_manager: PluginManager
    ):
        self.pipeline_repo = pipeline_repo
        self.engine_factory = engine_factory
        self.run_registry = run_registry
        self.cancellation_strategy = cancellation_strategy
        self.background_strategy = background_strategy
        self.plugin_manager = plugin_manager

    def start_execution(
        self, 
        pipeline_id: str, 
        version: str, 
        trigger_type: str, 
        parameters: Dict[str, Any]
    ) -> ExecutionRun:
        """
        Starts a new pipeline execution run.
        """
        # 1. Fetch metadata
        pipeline_version = self.pipeline_repo.get_pipeline_version(pipeline_id, version)
        if not pipeline_version:
            raise ValueError(f"Pipeline version {pipeline_id}:{version} not found.")

        graph = self.pipeline_repo.get_dependency_graph(pipeline_id, version)
        if not graph:
            raise ValueError(f"Dependency graph for {pipeline_id}:{version} not found.")

        import uuid
        run_id = f"run-{uuid.uuid4().hex[:8]}"

        run = ExecutionRun(
            id=run_id,
            pipeline_id=pipeline_id,
            pipeline_version_id=version,
            trigger_type=trigger_type,
            status=ExecutionState.PENDING
        )
        
        # 2. Persist initial state
        self.run_registry.create_run(run)

        # 3. Instantiate Engine components via factory
        coordinator = self.engine_factory.create_coordinator(pipeline_version, graph)
        coordinator.initialize_run(run)
        
        runner = self.engine_factory.create_runner(coordinator, self.plugin_manager)

        # 4. Dispatch to background
        self.background_strategy.submit(run_id, runner.run)
        
        return run

    def get_execution(self, run_id: str) -> ExecutionRun:
        """
        Retrieves the state of a run.
        """
        return self.run_registry.get_run(run_id)

    def cancel_execution(self, run_id: str) -> None:
        """
        Cancels an ongoing execution run.
        """
        self.cancellation_strategy.cancel(run_id)
