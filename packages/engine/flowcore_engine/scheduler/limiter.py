# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import threading

class ConcurrencyLimiter:
    """Thread-safe concurrent execution tracker."""
    
    def __init__(self, max_concurrent: int) -> None:
        self.max_concurrent = max_concurrent
        self._running_count = 0
        self._lock = threading.Lock()
        
    def acquire(self) -> bool:
        """Returns True if a slot is successfully acquired, False otherwise."""
        with self._lock:
            if self._running_count < self.max_concurrent:
                self._running_count += 1
                return True
            return False
            
    def release(self) -> None:
        """Releases a running slot."""
        with self._lock:
            if self._running_count > 0:
                self._running_count -= 1
                
    def running_count(self) -> int:
        with self._lock:
            return self._running_count
            
    def available_slots(self) -> int:
        with self._lock:
            return max(0, self.max_concurrent - self._running_count)
