from typing import Any, Dict, Optional
from flowcore_shared.schemas.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.application.cancellation import CancellationStrategy
from flowcore_server.application.background import BackgroundExecutionStrategy
from flowcore_server.application.engine_factory import ExecutionEngineFactory
from flowcore_engine.plugins.manager import PluginManager

from flowcore_server.application.interfaces.dispatcher import AbstractEventDispatcher
from flowcore_shared.events.domain import (
    PipelineExecutionStarted,
    PipelineExecutionCompleted,
    PipelineExecutionFailed,
    RunCancelled
)

class ExecutionService:
    """
    Core service wrapping engine execution and lifecycle management.
    Isolates the engine layer from HTTP routers.
    """
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        engine_factory: ExecutionEngineFactory,
        cancellation_strategy: CancellationStrategy,
        background_strategy: BackgroundExecutionStrategy,
        plugin_manager: PluginManager,
        event_dispatcher: AbstractEventDispatcher
    ):
        self.uow = uow
        self.engine_factory = engine_factory
        self.cancellation_strategy = cancellation_strategy
        self.background_strategy = background_strategy
        self.plugin_manager = plugin_manager
        self.event_dispatcher = event_dispatcher

    async def start_execution(
        self, 
        pipeline_id: str, 
        version: str, 
        trigger_type: str, 
        parameters: Dict[str, Any]
    ) -> ExecutionRun:
        """
        Starts a new pipeline execution run.
        """
        async with self.uow:
            # 1. Fetch metadata
            pipeline_version = await self.uow.pipelines.get_pipeline_version(pipeline_id, version)
            if not pipeline_version:
                raise ValueError(f"Pipeline version {pipeline_id}:{version} not found.")

            from flowcore_shared.schemas.dependencies.dependency_graph import DependencyGraph
            from flowcore_shared.schemas.dependencies.node import Node
            from flowcore_shared.schemas.dependencies.edge import Edge

            nodes = {step.step_id: Node(node_id=step.step_id) for step in pipeline_version.steps}
            edges = []
            for step in pipeline_version.steps:
                for dep in step.depends_on:
                    edges.append(Edge(source=dep, target=step.step_id))
            graph = DependencyGraph(nodes=nodes, edges=edges)

            import uuid
            run_id = f"run-{uuid.uuid4().hex[:8]}"

            run = ExecutionRun(
                id=run_id,
                pipeline_id=pipeline_id,
                pipeline_version_id=pipeline_version.id, # Must use the actual version ID here
                trigger_type=trigger_type,
                status=ExecutionState.PENDING
            )
            
            # 2. Persist initial state
            await self.uow.executions.create_run(run)
            await self.uow.commit()
            
            # Dispatch event AFTER successful commit
            event = PipelineExecutionStarted(
                run_id=run.id,
                pipeline_id=run.pipeline_id,
                pipeline_version_id=run.pipeline_version_id
            )
            await self.event_dispatcher.dispatch(event)

        # 3. Instantiate Engine components via factory
        coordinator = self.engine_factory.create_coordinator(pipeline_version, graph)
        coordinator.initialize_run(run)
        
        runner = self.engine_factory.create_runner(coordinator, self.plugin_manager)

        # 4. Dispatch to background via wrapper to handle completion events
        async def background_task():
            import asyncio
            import logging
            logger = logging.getLogger("flowcore")
            try:
                # Engine is synchronous, offload to thread
                await asyncio.to_thread(runner.run)
                await self.complete_execution(run.id)
            except Exception as e:
                logger.error(f"Background task failed: {e}", exc_info=True)
                await self.fail_execution(run.id, str(e))

        self.background_strategy.submit(run_id, background_task)
        
        return run

    async def get_execution(self, run_id: str) -> Optional[ExecutionRun]:
        """
        Retrieves the state of a run.
        """
        async with self.uow:
            return await self.uow.executions.get_run(run_id)

    async def cancel_execution(self, run_id: str) -> None:
        """
        Cancels an ongoing execution run.
        """
        async with self.uow:
            run = await self.uow.executions.get_run(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found.")
            await self.cancellation_strategy.cancel(run_id, self.uow)
            await self.uow.commit()

            # Emit event AFTER commit
            event = RunCancelled(
                run_id=run.id,
                pipeline_id=run.pipeline_id,
                pipeline_version_id=run.pipeline_version_id
            )
            await self.event_dispatcher.dispatch(event)

    async def complete_execution(self, run_id: str) -> None:
        """Called by background task when engine finishes successfully."""
        from datetime import datetime, timezone
        async with self.uow:
            run = await self.uow.executions.get_run(run_id)
            if not run:
                return
            
            run = run.model_copy(update={
                "status": ExecutionState.COMPLETED,
                "end_time": datetime.now(timezone.utc)
            })
            await self.uow.executions.save(run)
            await self.uow.commit()
            
            event = PipelineExecutionCompleted(
                run_id=run.id,
                pipeline_id=run.pipeline_id,
                pipeline_version_id=run.pipeline_version_id
            )
            await self.event_dispatcher.dispatch(event)

    async def fail_execution(self, run_id: str, error_message: str) -> None:
        """Called by background task when engine fails."""
        from datetime import datetime, timezone
        async with self.uow:
            run = await self.uow.executions.get_run(run_id)
            if not run:
                return
            
            run = run.model_copy(update={
                "status": ExecutionState.FAILED,
                "end_time": datetime.now(timezone.utc)
            })
            await self.uow.executions.save(run)
            await self.uow.commit()
            
            event = PipelineExecutionFailed(
                run_id=run.id,
                pipeline_id=run.pipeline_id,
                pipeline_version_id=run.pipeline_version_id,
                error_message=error_message
            )
            await self.event_dispatcher.dispatch(event)
