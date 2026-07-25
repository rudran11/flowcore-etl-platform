# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
import concurrent.futures
from typing import Dict
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.plugins.manager import PluginManager
from flowcore_engine.executor.base import AbstractExecutor
from flowcore_engine.executor.models import ExecutionResult
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
        executor: AbstractExecutor
    ) -> None:
        self.coordinator = coordinator
        self.plugin_manager = plugin_manager
        self.executor = executor
        
        # Maps Future -> ExecutionTask
        self._pending_futures: Dict[concurrent.futures.Future, ExecutionTask] = {}
        # Maps step_id -> Future (for tracking timeouts easily)
        self._step_to_future: Dict[str, concurrent.futures.Future] = {}

    def run(self) -> None:
        """
        Drives the execution loop until no pending work remains.
        """
        while self.coordinator.has_pending_work():
            # 1. Drain new tasks from the coordinator and submit them
            self._submit_available_tasks()
            
            if not self._pending_futures:
                # Nothing is running and nothing is queued.
                # If there's still "pending work", it means something is blocked or failed fast.
                break

            if self._pending_futures:
                # 2. Wait for at least one future to complete or a short timeout tick (for timeouts)
                done, not_done = concurrent.futures.wait(
                    self._pending_futures.keys(),
                    timeout=1.0,
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                # 3. Process completed futures
                for future in done:
                    task = self._pending_futures.pop(future)
                    del self._step_to_future[task.step_id]
                    self._process_completed_future(future, task)
                
            # 4. Enforce timeouts on running tasks
            # FUTURE ENHANCEMENT: Enforce timeout logic here by inspecting duration
            # Currently just relying on the executor or native cancellation mechanisms.

    def _submit_available_tasks(self) -> None:
        """Drains the coordinator's available tasks and submits them to the executor."""
        while True:
            task = self.coordinator.get_next_task()
            if task is None:
                break
                
            # Fetch plugin instance
            plugin = self.plugin_manager.get_plugin(task.plugin_id)
            
            # Submit to executor
            future = self.executor.submit(plugin.execute, task.runtime_context)
            
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
                self.coordinator.handle_event(ExecutionEventType.TASK_FAILED, task, payload=result.exception)
                
        except Exception as e:
            # Trapping any unexpected exceptions from the future itself
            self.coordinator.handle_event(ExecutionEventType.TASK_FAILED, task, payload=e)
