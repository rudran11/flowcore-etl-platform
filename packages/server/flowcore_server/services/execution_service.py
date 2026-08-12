from typing import Any, Dict, Optional
from flowcore.models.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.application.cancellation import CancellationStrategy
from flowcore_server.application.background import BackgroundExecutionStrategy
from flowcore_server.application.engine_factory import ExecutionEngineFactory
from flowcore.engine.plugins.manager import PluginManager

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

            pipeline = await self.uow.pipelines.get_pipeline(pipeline_id)
            if not pipeline:
                raise ValueError(f"Pipeline {pipeline_id} not found.")

            from flowcore.models.dependencies.dependency_graph import DependencyGraph
            from flowcore.models.dependencies.node import Node
            from flowcore.models.dependencies.edge import Edge

            nodes = {step.step_id: Node(node_id=step.step_id) for step in pipeline_version.steps}
            edges = []
            for step in pipeline_version.steps:
                for dep in step.depends_on:
                    edges.append(Edge(source=dep, target=step.step_id))
            graph = DependencyGraph(nodes=nodes, edges=edges)

            import uuid
            run_id = str(uuid.uuid4())

            run = ExecutionRun(
                id=run_id,
                workspace_id=pipeline.workspace_id,
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
        
        # Load environment context
        # For simplicity in MVP, we check if there are bound environments. If yes, take the first.
        # Ideally, `environment_id` would be passed in `parameters` from the API.
        env_vars = {}
        env_secrets = {}
        env_type = "DEVELOPMENT"
        
        async with self.uow:
            bound_envs = await self.uow.environments.get_bound_environments(pipeline_id)
            target_env_id = parameters.get("environment_id")
            
            if target_env_id:
                target_env = next((e for e in bound_envs if e.id == target_env_id), None)
            else:
                target_env = bound_envs[0] if bound_envs else None
                
            if target_env:
                from flowcore_server.services.environment_service import EnvironmentService
                env_service = EnvironmentService(self.uow)
                ctx = await env_service.get_environment_context(target_env.id)
                env_vars = ctx["variables"]
                env_secrets = ctx["secrets"]
                env_type = ctx["environment_type"]
                
        # Inject into coordinator run state so it's available when RuntimeContext is generated.
        # Wait, RuntimeContext is generated per step in the engine. Let's see how engine generates it.
        # Actually, ExecutionRun parameters can store these, but we don't want to store secrets in DB.
        # We can attach them to the coordinator so it can construct RuntimeContext.
        coordinator.env_vars = env_vars
        coordinator.env_secrets = env_secrets
        coordinator.env_type = env_type
        
        coordinator.state_change_callback = None
        
        runner = self.engine_factory.create_runner(coordinator, self.plugin_manager)

        # 4. Dispatch to background via wrapper to handle completion events
        async def background_task():
            import asyncio
            import logging
            logger = logging.getLogger("flowcore")
            try:
                # Engine is synchronous, offload to thread
                await asyncio.to_thread(runner.run)
                await self.complete_execution(run.id, final_run_state=coordinator._run)
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

    async def complete_execution(self, run_id: str, final_run_state: Optional[ExecutionRun] = None) -> None:
        """Called by background task when engine finishes successfully."""
        from datetime import datetime, timezone
        async with self.uow:
            if final_run_state:
                run = final_run_state
            else:
                run = await self.uow.executions.get_run(run_id)
            
            
            if not run:
                return
            
            # Determine overall status from steps
            has_failures = any(step.status in [ExecutionState.FAILED, ExecutionState.RETRYING] for step in run.steps.values())
            overall_status = ExecutionState.FAILED if has_failures else ExecutionState.COMPLETED
            
            run = run.model_copy(update={
                "status": overall_status,
                "end_time": datetime.now(timezone.utc)
            })
            await self.uow.executions.save(run)
            
            # Extract lineage from all steps
            all_inputs = []
            all_outputs = []
            for step in run.steps.values():
                lineage = step.outputs.get("_lineage", {})
                all_inputs.extend(lineage.get("input_datasets", []))
                all_outputs.extend(lineage.get("output_datasets", []))
                
            if all_inputs or all_outputs:
                from flowcore_server.services.lineage_service import LineageService
                from flowcore_shared.schemas.lineage.dataset import DatasetCreate, DatasetType
                lineage_service = LineageService(self.uow)
                
                # Convert to DatasetCreate objects
                input_ds = [DatasetCreate(name=ds["name"], type=DatasetType(ds["type"])) for ds in all_inputs]
                output_ds = [DatasetCreate(name=ds["name"], type=DatasetType(ds["type"])) for ds in all_outputs]
                
                await lineage_service.register_execution_lineage(
                    workspace_id=str(run.workspace_id),
                    execution_id=run.id,
                    inputs=input_ds,
                    outputs=output_ds
                )

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
                "end_time": datetime.now(timezone.utc),
                "error_message": error_message
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

    async def list_executions(
        self, 
        pipeline_id: Optional[str] = None, 
        status: Optional[str] = None, 
        limit: int = 25, 
        skip: int = 0
    ):
        """List executions with pagination and optional filters."""
        async with self.uow:
            return await self.uow.executions.list_runs(
                pipeline_id=pipeline_id,
                status=status,
                limit=limit,
                skip=skip
            )
