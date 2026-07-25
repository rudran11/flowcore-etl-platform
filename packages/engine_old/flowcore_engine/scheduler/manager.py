# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional
from .models import ScheduledTask
from .enums import InternalTaskStatus
from .queue import TaskQueue
from .limiter import ConcurrencyLimiter

class ExecutionScheduler:
    """
    Facade managing deterministic task ordering and concurrent execution limits.
    """
    
    def __init__(self, max_concurrent_tasks: int = 10) -> None:
        self._queue = TaskQueue()
        self._limiter = ConcurrencyLimiter(max_concurrent=max_concurrent_tasks)
        
    def submit_task(self, step_id: str, priority: int = 0) -> None:
        """Adds a task to the deterministic queue."""
        task = ScheduledTask(step_id=step_id, priority=priority, status=InternalTaskStatus.QUEUED)
        self._queue.push(task)
        
    def get_next_task(self) -> Optional[str]:
        """
        Attempts to acquire a concurrency slot and dispatch the next highest priority task.
        Returns the step_id if successful, or None if the queue is empty or limits are reached.
        """
        if self._limiter.acquire():
            task = self._queue.pop()
            if task is not None:
                task.status = InternalTaskStatus.DISPATCHED
                return task.step_id
            else:
                # Give back the slot if queue was empty
                self._limiter.release()
        return None
        
    def complete_task(self, step_id: str) -> None:
        """Marks a task as completed and frees a concurrency slot."""
        self._limiter.release()
        
    def fail_task(self, step_id: str) -> None:
        """Fails a task, freeing a concurrency slot."""
        self._limiter.release()
        
    def cancel(self, step_id: str) -> None:
        """Future extension point for canceling a queued or running task."""
        raise NotImplementedError("Task cancellation is reserved for future implementation.")
        
    def queue_size(self) -> int:
        """Returns the number of tasks currently queued."""
        return self._queue.size()
        
    def running_tasks(self) -> int:
        """Returns the current number of tasks consuming a concurrency slot."""
        return self._limiter.running_count()
        
    def available_slots(self) -> int:
        """Returns the number of slots available for immediate execution."""
        return self._limiter.available_slots()
