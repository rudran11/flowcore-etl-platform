# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
import concurrent.futures
from typing import Dict, Any
from flowcore.engine.coordinator.manager import ExecutionCoordinator
from flowcore.engine.plugins.manager import PluginManager
from flowcore.engine.executor.base import AbstractExecutor
from flowcore.engine.executor.models import ExecutionResult
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
from flowcore_shared.schemas.base.enums import ExecutionState
from .models import ExecutionTask
from .events import ExecutionEventType

class EngineRunner:
    """
    The main runtime loop for FlowCore execution.
    Consumes ExecutionTasks from the Coordinator, delegates them to the Executor,
    and returns lightweight events back to the Coordinator.
    Opaque boundary: Does not evaluate business logic or pipeline metadata.
    """

    def __init__(
        self,
        coordinator: ExecutionCoordinator,
        plugin_manager: PluginManager,
        executor: AbstractExecutor,
        state_store: Any = None
    ) -> None:
        self.coordinator = coordinator
        self.plugin_manager = plugin_manager
        self.executor = executor
        self.state_store = state_store
        
        # Maps Future -> ExecutionTask
        self._pending_futures: Dict[concurrent.futures.Future, ExecutionTask] = {}
        # Maps step_id -> Future (for tracking timeouts easily)
        self._step_to_future: Dict[str, concurrent.futures.Future] = {}

    def run(self) -> None:
        """
        Drives the execution loop until no pending work remains.
        """
        self._retrying_futures = {}
        
        while self.coordinator.has_pending_work() or self._retrying_futures:
            # Check for global cancellation
            if hasattr(self.coordinator, 'cancellation_event') and self.coordinator.cancellation_event and self.coordinator.cancellation_event.is_set():
                break

            # 1. Drain new tasks from the coordinator and submit them
            self._submit_available_tasks()
            
            if not self._pending_futures and not self._retrying_futures:
                # Nothing is running and nothing is queued.
                # If there's still "pending work", it means something is blocked or failed fast.
                break

            all_futures = list(self._pending_futures.keys()) + list(self._retrying_futures.keys())
            if all_futures:
                # 2. Wait for at least one future to complete or a short timeout tick (for timeouts)
                done, not_done = concurrent.futures.wait(
                    all_futures,
                    timeout=1.0,
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                # 3. Process completed futures
                for future in done:
                    if future in self._retrying_futures:
                        task = self._retrying_futures.pop(future)
                        # Re-submit to the queue (remains in RETRYING state until TASK_STARTED)
                        self.coordinator.scheduler.submit_task(task.step_id)
                    elif future in self._pending_futures:
                        task = self._pending_futures.pop(future)
                        del self._step_to_future[task.step_id]
                        self._process_completed_future(future, task)
                
            # 4. Enforce timeouts on running tasks
            # FUTURE ENHANCEMENT: Enforce timeout logic here by inspecting duration
            # Currently just relying on the executor or native cancellation mechanisms.
            
        return self.coordinator._run

    def _submit_available_tasks(self) -> None:
        """Drains the coordinator's available tasks and submits them to the executor."""
        while True:
            task = self.coordinator.get_next_task()
            if task is None:
                break
                
            # Fetch plugin instance
            plugin = self.plugin_manager.get_plugin(task.plugin_id)
            
            # Determine if task is a terminal node (no downstream dependencies)
            is_terminal = len(self.coordinator._adj_list.get(task.step_id, [])) == 0

            # Wrapper to execute and optionally consume the final stream
            def _execute_and_drain(plugin_instance, context, terminal: bool, pipeline_id: str, step_id: str):
                result = plugin_instance.execute(context)
                
                metrics = {}
                final_schema = None
                
                # Preview tracking
                preview_records = []
                preview_schema = None
                preview_errors = []
                is_preview = context.preview_context.is_preview
                limit = context.preview_context.record_limit
                cancellation_event = getattr(context, 'cancellation_event', context.preview_context.cancellation_event)
                
                print(f"[PREVIEW DEBUG] Processing step {step_id}, is_preview: {is_preview}")
                
                import inspect
                if terminal:
                    if inspect.isgenerator(result) or (hasattr(result, '__iter__') and not isinstance(result, (dict, list, str, tuple, set))):
                        for msg in result:
                            if cancellation_event.is_set():
                                break
                                
                            if getattr(msg, 'type', None) == MessageType.STATE and getattr(msg, 'state', None) and self.state_store:
                                self.state_store.set_state(pipeline_id, step_id, msg.state.state_data)
                            elif getattr(msg, 'type', None) == MessageType.SCHEMA and getattr(msg, 'schema_info', None):
                                final_schema = msg.schema_info.schema_data
                                if is_preview:
                                    preview_schema = final_schema
                            elif getattr(msg, 'type', None) == MessageType.LOG and getattr(msg, 'log', None):
                                if "metrics:" in msg.log.message:
                                    metrics[msg.log.message.split("metrics:")[0].strip()] = msg.log.message.split("metrics:")[1].strip()
                                elif is_preview and getattr(msg.log, 'level', 'INFO') == 'ERROR':
                                    preview_errors.append(msg.log.message)
                            elif getattr(msg, 'type', None) == MessageType.RECORD and getattr(msg, 'record', None):
                                if is_preview:
                                    if len(preview_records) < limit:
                                        preview_records.append(msg.record.data)
                                    else:
                                        cancellation_event.set()
                                        break
                                        
                        # Update step state with preview data if applicable
                        if is_preview and self.coordinator._run and step_id in self.coordinator._run.steps:
                            step_run = self.coordinator._run.steps[step_id]
                            print(f"[PREVIEW DEBUG] Terminal node {step_id} drained {len(preview_records)} records")
                            new_outputs = {
                                **step_run.outputs, 
                                "metrics": {**(step_run.outputs.get("metrics") or {}), **metrics},
                                "_preview_records": preview_records,
                                "_preview_schema": preview_schema,
                                "_preview_errors": preview_errors
                            }
                            self.coordinator._run.steps[step_id] = step_run.model_copy(update={"outputs": new_outputs})
                            
                        return {"status": "drained", "metrics": metrics, "final_schema": final_schema, "_preview_records": preview_records}
                    return result
                else:
                    if inspect.isgenerator(result) or (hasattr(result, '__iter__') and not isinstance(result, (dict, list, str, tuple, set))):
                        def intercepting_generator():
                            records_passed = 0
                            preview_schema = None
                            for msg in result:
                                if cancellation_event.is_set():
                                    break
                                    
                                if getattr(msg, 'type', None) == MessageType.SCHEMA and getattr(msg, 'schema_info', None) and is_preview:
                                    preview_schema = msg.schema_info.schema_data
                                elif getattr(msg, 'type', None) == MessageType.LOG and getattr(msg, 'log', None):
                                    if "metrics:" in msg.log.message:
                                        k = msg.log.message.split("metrics:")[0].strip()
                                        v = msg.log.message.split("metrics:")[1].strip()
                                        metrics[k] = v
                                    elif is_preview and getattr(msg.log, 'level', 'INFO') == 'ERROR':
                                        preview_errors.append(msg.log.message)
                                elif getattr(msg, 'type', None) == MessageType.RECORD and getattr(msg, 'record', None) and is_preview:
                                    if len(preview_records) < limit:
                                        preview_records.append(msg.record.data)
                                    records_passed += 1
                                        
                                yield msg
                                
                                if is_preview and records_passed >= context.preview_context.execution_limit:
                                    cancellation_event.set()
                                    break
                                
                            if is_preview and self.coordinator._run and step_id in self.coordinator._run.steps:
                                step_run = self.coordinator._run.steps[step_id]
                                print(f"[PREVIEW DEBUG] Non-terminal node {step_id} intercepted {len(preview_records)} records")
                                new_outputs = {
                                    **step_run.outputs, 
                                    "metrics": {**(step_run.outputs.get("metrics") or {}), **metrics},
                                    "_preview_records": preview_records,
                                    "_preview_schema": preview_schema,
                                    "_preview_errors": preview_errors
                                }
                                self.coordinator._run.steps[step_id] = step_run.model_copy(update={"outputs": new_outputs})
                                if self.coordinator.state_change_callback:
                                    self.coordinator.state_change_callback()
                                    
                        return intercepting_generator()
                    return result

            # Submit to executor
            future = self.executor.submit(
                _execute_and_drain, 
                plugin, 
                task.runtime_context, 
                is_terminal,
                task.runtime_context.pipeline_id,
                task.step_id
            )
            
            # Track
            self._pending_futures[future] = task
            self._step_to_future[task.step_id] = future
            
            # Emit TASK_STARTED event
            self.coordinator.handle_event(ExecutionEventType.TASK_STARTED, task)

    def _process_completed_future(self, future: concurrent.futures.Future, task: ExecutionTask) -> None:
        """Processes an execution result, emitting either COMPLETED or FAILED."""
        try:
            result: ExecutionResult = future.result()
            
            if result.success:
                self.coordinator.handle_event(ExecutionEventType.TASK_COMPLETED, task, payload=result)
            else:
                import traceback
                if result.exception:
                    print(f"[PREVIEW DEBUG] Task {task.step_id} failed natively with error: {str(result.exception)}")
                backoff = self.coordinator.handle_event(ExecutionEventType.TASK_FAILED, task, payload=result.exception)
                if backoff is not None:
                    import time
                    print(f"[PREVIEW DEBUG] Retrying Task {task.step_id} in {backoff} seconds...")
                    retry_future = self.executor.submit(time.sleep, backoff)
                    self._retrying_futures[retry_future] = task
                    
        except Exception as e:
            # Trapping any unexpected exceptions from the future itself
            import traceback
            traceback.print_exc()
            print(f"[PREVIEW DEBUG] Task {task.step_id} failed with error: {str(e)}")
            backoff = self.coordinator.handle_event(ExecutionEventType.TASK_FAILED, task, payload=e)
            if backoff is not None:
                import time
                print(f"[PREVIEW DEBUG] Retrying Task {task.step_id} in {backoff} seconds...")
                retry_future = self.executor.submit(time.sleep, backoff)
                self._retrying_futures[retry_future] = task
