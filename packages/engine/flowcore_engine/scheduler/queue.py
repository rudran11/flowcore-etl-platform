# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import heapq
import threading
from typing import Optional
from .models import ScheduledTask

class TaskQueue:
    """Thread-safe deterministic priority queue."""
    
    def __init__(self) -> None:
        self._queue: list[ScheduledTask] = []
        self._lock = threading.Lock()
        
    def push(self, task: ScheduledTask) -> None:
        with self._lock:
            heapq.heappush(self._queue, task)
            
    def pop(self) -> Optional[ScheduledTask]:
        with self._lock:
            if not self._queue:
                return None
            return heapq.heappop(self._queue)
            
    def size(self) -> int:
        with self._lock:
            return len(self._queue)
