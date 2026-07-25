from abc import ABC, abstractmethod
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.runner.engine import EngineRunner
from flowcore.engine.executor.base import AbstractExecutor
from flowcore.engine.executor.thread import ThreadExecutor
from flowcore.engine.plugins.manager import PluginManager
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.dependencies.dependency_graph import DependencyGraph

class ExecutionEngineFactory(ABC):
    """
    Factory for instantiating core execution engine components.
    Ensures the service layer remains unaware of engine construction details.
    """
    @abstractmethod
    def create_coordinator(self, pipeline: PipelineVersion, graph: DependencyGraph) -> ExecutionCoordinator:
        pass

    @abstractmethod
    def create_runner(self, coordinator: ExecutionCoordinator, plugin_manager: PluginManager) -> EngineRunner:
        pass

class DefaultExecutionEngineFactory(ExecutionEngineFactory):
    """
    Default factory using ThreadExecutor.
    """
    def create_coordinator(self, pipeline: PipelineVersion, graph: DependencyGraph) -> ExecutionCoordinator:
        return ExecutionCoordinator(pipeline=pipeline, graph=graph)

    def create_runner(self, coordinator: ExecutionCoordinator, plugin_manager: PluginManager) -> EngineRunner:
        executor = ThreadExecutor(max_workers=10)
        return EngineRunner(
            coordinator=coordinator,
            plugin_manager=plugin_manager,
            executor=executor
        )
