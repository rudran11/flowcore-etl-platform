# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from dataclasses import dataclass
from .enums import InternalTaskStatus

@dataclass
class ScheduledTask:
    """Represents a unit of work within the scheduler."""
    step_id: str
    priority: int = 0
    status: InternalTaskStatus = InternalTaskStatus.QUEUED
    
    def __lt__(self, other: "ScheduledTask") -> bool:
        """
        Determines the priority order in the queue.
        Higher priority integer means higher precedence.
        If priority is equal, alphabetical step_id resolves ties for absolute determinism.
        """
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.step_id < other.step_id
