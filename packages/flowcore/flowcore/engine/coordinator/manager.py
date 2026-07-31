# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Dict, List, Optional, Any
from flowcore.models.pipeline.pipeline_version import PipelineVersion
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore.models.pipeline.retry import RetryPolicy
from flowcore.engine.scheduler.manager import ExecutionScheduler
from flowcore.engine.state.manager import StateManager
from flowcore.engine.state.store import AbstractStateStore
from flowcore.engine.retry.manager import RetryManager
from flowcore.engine.exceptions.base import EngineError

class ExecutionCoordinator:
    """
    The orchestrator that acts as the brain of the Execution Engine.
    It manages the lifecycle of a single PipelineVersion execution by
    coordinating the StateManager, RetryManager, and ExecutionScheduler.

    FUTURE EXTENSION:
    ExecutionSummary support will be added in a future milestone containing:
    - total_steps, completed_steps, failed_steps, retried_steps, execution_duration

    FAILURE POLICY:
    Milestone 3 implements a strict "Fail Fast" policy.
    A FatalPluginError (or exhausting retries) prevents downstream scheduling.
    """

    def __init__(self, pipeline: PipelineVersion, graph: DependencyGraph, max_concurrent: int = 10, state_store: AbstractStateStore = None) -> None:
        self.pipeline = pipeline
        self.graph = graph
        self.scheduler = ExecutionScheduler(max_concurrent_tasks=max_concurrent)
        self.state_change_callback = None
        self.state_store = state_store
        
        # Private working structures to preserve immutability of the metadata layer
        self._step_states: Dict[str, ExecutionState] = {}
        self._remaining_indegree: Dict[str, int] = {}
        self._adj_list: Dict[str, List[str]] = {}
        self._attempts: Dict[str, int] = {}
        self._run: Optional[ExecutionRun] = None
        self._in_edges: Dict[str, List[str]] = {}
        self._step_outputs: Dict[str, Any] = {}
        
        # Hydrate adjacency and in-degrees from the graph
        for node_id in self.graph.nodes:
            self._step_states[node_id] = ExecutionState.PENDING
            self._remaining_indegree[node_id] = 0
            self._adj_list[node_id] = []
            self._in_edges[node_id] = []
            self._attempts[node_id] = 0
            
        for edge in self.graph.edges:
            self._remaining_indegree[edge.target] += 1
            self._adj_list[edge.source].append(edge.target)
            self._in_edges[edge.target].append(edge.source)

    def initialize_run(self, run: ExecutionRun) -> ExecutionRun:
        """Initializes runtime state and primes the scheduler with initial steps."""
        self._run = run.model_copy(update={
            "status": StateManager.transition(run.status, ExecutionState.QUEUED)
        })
        
        # Push all 0-degree steps to the scheduler
        for step_id, degree in self._remaining_indegree.items():
            if degree == 0:
                self._transition_step(step_id, ExecutionState.QUEUED)
                self.scheduler.submit_task(step_id)
                
        return self._run

    def has_pending_work(self) -> bool:
        """
        Returns True if there are tasks still executing or waiting to execute.
        This allows an external executor loop to iterate cleanly.
        """
        return self.scheduler.queue_size() > 0 or self.scheduler.running_tasks() > 0

    def get_next_task(self) -> Optional["ExecutionTask"]:
        """Retrieves the next unblocked step as an ExecutionTask."""
        step_id = self.scheduler.get_next_task()
        if not step_id:
            return None
            
        step_metadata = next((s for s in self.pipeline.steps if s.step_id == step_id), None)
        if not step_metadata:
            # Failsafe
            return None
            
        from flowcore.engine.context.runtime import RuntimeContext
        from flowcore.engine.runner.models import ExecutionTask
        from datetime import datetime
        import logging
        
        # Inject message_stream if there's an upstream dependency (Linear pipeline assumption for now)
        upstream_ids = self._in_edges.get(step_id, [])
        message_stream = None
        if upstream_ids:
            upstream_id = upstream_ids[0]
            if upstream_id in self._step_outputs:
                message_stream = self._step_outputs[upstream_id]
                
        # Inject state from store if available
        step_state = {}
        if self.state_store:
            step_state = self.state_store.get_state(self.pipeline.pipeline_id, step_id) or {}
        
        context = RuntimeContext(
            run_id=self._run.id if self._run else "unknown",
            pipeline_id=self.pipeline.pipeline_id,
            step_id=step_id,
            execution_start_time=datetime.now(),
            environment=getattr(self, 'env_type', 'DEVELOPMENT'),
            working_directory="/tmp/flowcore/work",
            temporary_directory="/tmp/flowcore/temp",
            parameters=step_metadata.parameters,
            variables=getattr(self, 'env_vars', {}),
            secrets=getattr(self, 'env_secrets', {}),
            logger=logging.getLogger(f"flowcore.step.{step_id}"),
            message_stream=message_stream,
            state=step_state
        )
        
        return ExecutionTask(
            step_id=step_id,
            plugin_id=step_metadata.connector_id,
            runtime_context=context,
            retry_attempt=self._attempts[step_id],
            timeout_seconds=None # Future enhancement
        )

    def handle_event(self, event_type: "ExecutionEventType", task: "ExecutionTask", payload: Any = None) -> None:
        """
        Consumes lightweight internal events emitted by the EngineRunner.
        """
        from flowcore.engine.runner.events import ExecutionEventType
        
        if event_type == ExecutionEventType.TASK_STARTED:
            self.on_step_started(task.step_id)
        elif event_type == ExecutionEventType.TASK_COMPLETED:
            self.on_step_completed(task, payload)
        elif event_type == ExecutionEventType.TASK_FAILED:
            # payload is the EngineError
            self.on_step_failed(task.step_id, payload)
        elif event_type == ExecutionEventType.TASK_TIMEOUT:
            # Future enhancement
            from flowcore.engine.exceptions.plugin import RecoverablePluginError
            self.on_step_failed(task.step_id, RecoverablePluginError("Task timeout exceeded"))

    def on_step_started(self, step_id: str) -> None:
        """Called when an executor acquires a step."""
        self._transition_step(step_id, ExecutionState.RUNNING)
        self._attempts[step_id] += 1

    def on_step_completed(self, task: "ExecutionTask", payload: Any = None) -> None:
        """Called when an executor finishes a step successfully."""
        step_id = task.step_id
        # Note: ExecutionResult returns `output` not `outputs`.
        plugin_output = payload.output if payload and hasattr(payload, 'output') else None
        
        outputs = {}
        import inspect
        if inspect.isgenerator(plugin_output) or (hasattr(plugin_output, '__iter__') and not isinstance(plugin_output, (dict, list, str, tuple, set))):
            # It's a stream/iterator. Store in memory, do not put in Pydantic DB model.
            self._step_outputs[step_id] = plugin_output
            outputs["stream"] = "active"
        else:
            self._step_outputs[step_id] = plugin_output
            if isinstance(plugin_output, dict):
                outputs = plugin_output
            elif hasattr(plugin_output, '__dict__'):
                outputs = plugin_output.__dict__.copy()
            else:
                outputs = {"result": plugin_output}
            
        # Capture lineage datasets
        lineage = {
            "input_datasets": task.runtime_context.input_datasets,
            "output_datasets": task.runtime_context.output_datasets
        }
        outputs["_lineage"] = lineage

        self._transition_step(step_id, ExecutionState.COMPLETED, outputs=outputs)
        self.scheduler.complete_task(step_id)
        
        # Eagerly unblock downstream neighbors
        for neighbor in self._adj_list.get(step_id, []):
            self._remaining_indegree[neighbor] -= 1
            if self._remaining_indegree[neighbor] == 0:
                self._transition_step(neighbor, ExecutionState.QUEUED)
                self.scheduler.submit_task(neighbor)

    def on_step_failed(self, step_id: str, error: EngineError) -> Optional[float]:
        """
        Called when a step fails. Evaluates retry eligibility.
        Returns the backoff duration (float) if the step will be retried, None otherwise.
        """
        # Resolve policy
        step_metadata = next((s for s in self.pipeline.steps if s.step_id == step_id), None)
        policy = (step_metadata.retry_policy if step_metadata and step_metadata.retry_policy else RetryPolicy())
        
        current_attempt = self._attempts[step_id]
        error_msg = str(error)
        
        if RetryManager.should_retry(error, current_attempt, policy):
            self._transition_step(step_id, ExecutionState.RETRYING, error_message=error_msg)
            self.scheduler.fail_task(step_id) # Release concurrency slot
            backoff = RetryManager.calculate_backoff(current_attempt, policy)
            # Future: the executor uses this backoff, then re-queues the step.
            return backoff
        else:
            self._transition_step(step_id, ExecutionState.FAILED, error_message=error_msg)
            self.scheduler.fail_task(step_id)
            # Fail fast: Downstream steps remain PENDING indefinitely (blocking execution).
            return None

    def _transition_step(self, step_id: str, target: ExecutionState, error_message: str = None, logs: list = None, outputs: dict = None) -> None:
        """Internal helper to safely transition a step's state."""
        current = self._step_states[step_id]
        new_state = StateManager.transition(current, target)
        self._step_states[step_id] = new_state
        
        if self._run:
            from datetime import datetime
            from flowcore.models.operational.execution import ExecutionStepRun
            import uuid
            
            if step_id not in self._run.steps:
                self._run.steps[step_id] = ExecutionStepRun(
                    id=str(uuid.uuid4()),
                    step_id=step_id,
                    status=new_state
                )
            
            step = self._run.steps[step_id]
            updates = {
                "status": new_state,
                "retry_count": self._attempts[step_id]
            }
            
            if new_state == ExecutionState.RUNNING and not step.start_time:
                updates["start_time"] = datetime.utcnow()
            elif new_state in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]:
                updates["end_time"] = datetime.utcnow()
                
            if error_message is not None:
                updates["error_message"] = error_message
            if logs is not None:
                updates["logs"] = step.logs + logs
            if outputs is not None:
                updates["outputs"] = {**step.outputs, **outputs}
                
            self._run.steps[step_id] = step.model_copy(update=updates)
                
            if self.state_change_callback:
                self.state_change_callback()
        
    def get_step_state(self, step_id: str) -> ExecutionState:
        """Returns the current state of a step."""
        return self._step_states[step_id]
