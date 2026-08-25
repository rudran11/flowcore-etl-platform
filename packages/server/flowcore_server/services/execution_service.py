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
        event_dispatcher: AbstractEventDispatcher,
        concurrency_manager: 'ConcurrencyManager' = None
    ):
        self.uow = uow
        self.engine_factory = engine_factory
        self.cancellation_strategy = cancellation_strategy
        self.background_strategy = background_strategy
        self.plugin_manager = plugin_manager
        self.event_dispatcher = event_dispatcher
        
        # If not provided, instantiate it
        if concurrency_manager is None:
            from flowcore_server.services.concurrency import ConcurrencyManager
            concurrency_manager = ConcurrencyManager(self.uow)
        self.concurrency_manager = concurrency_manager

        # We can fetch cancellation controller from the cancellation strategy if it is DefaultCancellationStrategy
        self.cancellation_controller = None
        if hasattr(self.cancellation_strategy, 'controller'):
            self.cancellation_controller = self.cancellation_strategy.controller

    async def start_execution(
        self, 
        pipeline_id: str, 
        version: str, 
        trigger_type: str, 
        parameters: Dict[str, Any],
        trigger_context: Dict[str, Any] = None
    ) -> ExecutionRun:
        """
        Starts a new pipeline execution run.
        """
        async with self.uow:
            # 1. Fetch metadata
            if version == "latest":
                versions = await self.uow.pipelines.list_pipeline_versions(pipeline_id)
                if not versions:
                    raise ValueError(f"No versions found for pipeline {pipeline_id}.")
                pipeline_version = versions[0]
            else:
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

            # Fetch workspace to get max_concurrent_runs
            workspace = await self.uow.workspaces.get(pipeline.workspace_id)
            max_concurrent_runs = workspace.max_concurrent_runs if workspace else 10

            from flowcore_server.services.concurrency import PipelineConcurrencyRejected
            try:
                # Concurrency policy is stored in the version's DSL definition JSON
                policy_str = pipeline_version.dsl_definition.get("concurrency_policy", "ALLOW")
                from flowcore_shared.schemas.base.enums import ConcurrencyPolicy
                try:
                    policy = ConcurrencyPolicy(policy_str)
                except ValueError:
                    policy = ConcurrencyPolicy.ALLOW

                initial_status = await self.concurrency_manager.evaluate_run(
                    workspace_id=pipeline.workspace_id,
                    pipeline_id=pipeline_id,
                    policy=policy,
                    max_workspace_runs=max_concurrent_runs
                )
            except PipelineConcurrencyRejected as e:
                raise ValueError(str(e))

            import uuid
            run_id = str(uuid.uuid4())

            run = ExecutionRun(
                id=run_id,
                workspace_id=pipeline.workspace_id,
                pipeline_id=pipeline_id,
                pipeline_version_id=pipeline_version.id,
                trigger_type=trigger_type,
                trigger_context=trigger_context or {},
                status=initial_status,
                start_time=None, # Only set when RUNNING
                end_time=None,
                steps={}
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

        if run.status == ExecutionState.QUEUED:
            return run

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
        
        # Inject global cancellation event
        if self.cancellation_controller:
            cancellation_event = self.cancellation_controller.register(run_id)
            coordinator.cancellation_event = cancellation_event
        
        runner = self.engine_factory.create_runner(coordinator, self.plugin_manager)

        # 4. Dispatch to background via wrapper to handle completion events
        async def background_task():
            import asyncio
            import logging
            logger = logging.getLogger("flowcore")
            try:
                # Engine is synchronous, offload to thread
                await asyncio.to_thread(runner.run)
                if self.cancellation_controller:
                    self.cancellation_controller.unregister(run_id)
                import json
                logger.info("FINAL RUN STATE STEPS OUTPUTS:")
                for sid, s in coordinator._run.steps.items():
                    logger.info(f"Step {sid}: {json.dumps(s.outputs)}")
                await self.complete_execution(run.id, final_run_state=coordinator._run)
            except Exception as e:
                logger.error(f"Background task failed: {e}", exc_info=True)
                await self.fail_execution(run.id, str(e)); import traceback; open("d:/FlowCore/flowcore-etl-platform/error.txt", "w").write(traceback.format_exc())

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
            await self._check_queued_runs(run.pipeline_id)

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
            await self._check_queued_runs(run.pipeline_id)

    async def _check_queued_runs(self, pipeline_id: str) -> None:
        """Helper to release queued runs for a pipeline after completion or failure."""
        next_run_id = await self.concurrency_manager.release_and_dequeue(pipeline_id)
        if next_run_id:
            import asyncio
            async def start_queued_run():
                async with self.uow:
                    queued_run = await self.uow.executions.get_run(next_run_id)
                    if not queued_run:
                        return
                    updated_run = queued_run.model_copy(update={'status': ExecutionState.PENDING})
                    await self.uow.executions.save(updated_run)
                    await self.uow.commit()
                # Ideally we call start_execution with the queued parameters.
                # Since start_execution creates a NEW run, we should probably refactor to execute an existing run.
                # For M18 MVP, updating status to PENDING and returning is enough to "unblock" it for a scheduler.
                pass 
                
            asyncio.create_task(start_queued_run())

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

    async def preview_execution(
        self, 
        request: Any, 
        workspace_id: str
    ) -> Any:
        from flowcore.models.dependencies.dependency_graph import DependencyGraph
        from flowcore.models.dependencies.node import Node
        from flowcore.models.dependencies.edge import Edge
        from flowcore.models.operational.execution import ExecutionRun
        from flowcore_server.models.execution import PreviewResponse
        from flowcore.engine.context.runtime import PreviewExecutionContext
        from flowcore.models.pipeline.pipeline_version import PipelineVersion
        from flowcore.models.pipeline.execution_step import ExecutionStep
        import uuid
        import asyncio
        import copy

        pipeline_version = request.pipeline

        # Prune DAG using reverse BFS from preview_node_id to find ancestors
        ancestors = set()
        queue = [request.preview_node_id]
        
        # Build reverse adjacency list
        reverse_adj = {}
        for step in pipeline_version.steps:
            reverse_adj[step.step_id] = step.depends_on
            
        if request.preview_node_id not in reverse_adj:
            return PreviewResponse(
                success=False, 
                error_message=f"Node {request.preview_node_id} not found in pipeline"
            )

        while queue:
            current = queue.pop(0)
            if current not in ancestors:
                ancestors.add(current)
                queue.extend(reverse_adj.get(current, []))

        # Build pruned graph
        nodes = {step_id: Node(node_id=step_id) for step_id in ancestors}
        edges = []
        pruned_steps = []
        for step in pipeline_version.steps:
            if step.step_id in ancestors:
                # Security Check: Reject destinations
                plugin = self.plugin_manager.get_plugin(step.plugin_id)
                if not plugin:
                    return PreviewResponse(success=False, error_message=f"Plugin {step.plugin_id} not found")
                
                from flowcore_shared.plugins.models import PluginType
                if plugin.metadata.connector_type == "Destination":
                    return PreviewResponse(
                        success=False, 
                        error_message="Previewing destination plugins is not allowed for safety"
                    )
                
                pruned_steps.append(step)
                for dep in step.depends_on:
                    if dep in ancestors:
                        edges.append(Edge(source=dep, target=step.step_id))

        graph = DependencyGraph(nodes=nodes, edges=edges)
        
        # Convert to proper PipelineVersion model expected by engine
        engine_steps = []
        for step in pruned_steps:
            engine_steps.append(ExecutionStep(
                step_id=step.step_id,
                connector_id=step.plugin_id,
                depends_on=step.depends_on,
                parameters=step.parameters
            ))

        mock_pipeline_version = PipelineVersion(
            id="preview-version",
            pipeline_id="preview-pipeline",
            version="preview",
            steps=engine_steps,
            dsl_definition=pipeline_version.dsl_definition,
            graph_definition=pipeline_version.graph_definition
        )

        # Generate ephemeral run ID
        run_id = str(uuid.uuid4())
        run = ExecutionRun(
            id=run_id,
            workspace_id=workspace_id or "default",
            pipeline_id="preview-pipeline",
            pipeline_version_id="preview-version",
            trigger_type="PREVIEW",
            status=ExecutionState.PENDING
        )

        coordinator = self.engine_factory.create_coordinator(mock_pipeline_version, graph)
        coordinator.initialize_run(run)
        
        coordinator.env_vars = {}
        coordinator.env_secrets = {}
        coordinator.env_type = "PREVIEW"
        coordinator.state_change_callback = None
        coordinator.preview_context = PreviewExecutionContext(
            is_preview=True,
            record_limit=request.limit or 50
        )
        coordinator.preview_context = PreviewExecutionContext(is_preview=True, record_limit=request.limit)
        
        runner = self.engine_factory.create_runner(coordinator, self.plugin_manager)

        try:
            # Execute synchronously with strict timeout
            await asyncio.wait_for(asyncio.to_thread(runner.run), timeout=15.0)
            
            # Extract preview data from the target node
            final_run_state = coordinator._run
            if not final_run_state or request.preview_node_id not in final_run_state.steps:
                return PreviewResponse(success=False, error_message="Preview execution failed to produce state")
                
            step_state = final_run_state.steps[request.preview_node_id]
            outputs = step_state.outputs
            
            input_records = []
            output_records = []
            
            # Since preview node is the terminal node of the pruned DAG, its intercepting_generator
            # will not be executed unless it has downstream nodes.
            # Wait, if it has no downstream nodes, it IS terminal, meaning _execute_and_drain handles it.
            # `outputs` contains `_preview_records`, `_preview_schema`, etc.
            # Actually, `outputs` in the terminal node handles the outputs!
            # What about the upstream nodes? They were non-terminal, so they were handled by intercepting_generator,
            # which ALSO populates `_preview_records`!
            # So `input_records` are the `_preview_records` of the UPSTREAM nodes.
            
            upstream_nodes = reverse_adj.get(request.preview_node_id, [])
            input_schema = None
            if upstream_nodes:
                # Just take the first upstream for simple pipelines
                up_id = upstream_nodes[0]
                up_state = final_run_state.steps.get(up_id)
                if up_state:
                    input_records = up_state.outputs.get("_preview_records", [])
                    input_schema = up_state.outputs.get("_preview_schema")
            
            # Output records are the node's own _preview_records (since it's terminal and we modified terminal drain)
            output_records = outputs.get("_preview_records", [])
            
            # Check if preview node failed
            if step_state.status == ExecutionState.FAILED:
                return PreviewResponse(
                    success=False,
                    error_message=f"Execution failed: {step_state.error_message}"
                )

            return PreviewResponse(
                success=True,
                metrics=outputs.get("metrics", {}),
                input_schema=input_schema,
                output_schema=outputs.get("_preview_schema") or outputs.get("final_schema"),
                input_records=input_records,
                output_records=output_records,
                errors=outputs.get("_preview_errors", [])
            )
            
        except asyncio.TimeoutError:
            coordinator.preview_context.cancellation_event.set()
            return PreviewResponse(success=False, error_message="Preview execution timed out (exceeded 15s)")
        except Exception as e:
            coordinator.preview_context.cancellation_event.set()
            import traceback
            return PreviewResponse(success=False, error_message=f"Preview execution failed: {str(e)}\n{traceback.format_exc()}")
