# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from enum import Enum

class InternalTaskStatus(str, Enum):
    """
    Lightweight internal scheduler status for a task.
    This does NOT replace the global ExecutionState. It is strictly for queue management.
    """
    QUEUED = "QUEUED"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
