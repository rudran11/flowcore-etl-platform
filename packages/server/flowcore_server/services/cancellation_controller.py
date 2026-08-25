# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import threading
from typing import Dict

class CancellationController:
    """
    In-memory registry of cancellation events for currently running execution runs.
    Provides a thread-safe way to cooperatively cancel background engine tasks.
    """
    def __init__(self):
        self._registry: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def register(self, run_id: str) -> threading.Event:
        """Registers a new run and returns its cancellation event."""
        event = threading.Event()
        with self._lock:
            self._registry[run_id] = event
        return event

    def unregister(self, run_id: str):
        """Removes a run from the registry upon completion."""
        with self._lock:
            self._registry.pop(run_id, None)

    def cancel(self, run_id: str) -> bool:
        """
        Sets the cancellation event for a given run if it is active.
        Returns True if the run was found and signaled, False otherwise.
        """
        with self._lock:
            event = self._registry.get(run_id)
            if event:
                event.set()
                return True
        return False
