# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import ABC, abstractmethod
from typing import Callable, Any
from concurrent.futures import Future
from datetime import datetime, timezone
from .models import ExecutionResult

class AbstractExecutor(ABC):
    """
    Abstract interface for all FlowCore Executors.

    BUSINESS LOGIC BOUNDARY:
    Executors execute callables only.
    Executors never perform:
    - retries
    - state transitions
    - scheduling
    - pipeline decisions
    Those remain the strict responsibility of the ExecutionCoordinator.
    """

    @abstractmethod
    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[ExecutionResult]:
        """Submits a task for execution."""
        pass

    @abstractmethod
    def shutdown(self, wait: bool = True) -> None:
        """Shuts down the executor."""
        pass

    def __enter__(self) -> "AbstractExecutor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.shutdown(wait=True)

    @staticmethod
    def _execute_wrapped(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> ExecutionResult:
        """
        Wraps the user-provided callable to standardize the ExecutionResult.
        Captures timing and exceptions gracefully.
        """
        started_at = datetime.now(timezone.utc)
        output = None
        exception = None
        success = False

        try:
            output = fn(*args, **kwargs)
            success = True
        except Exception as e:
            exception = e
        finally:
            finished_at = datetime.now(timezone.utc)
            duration_ms = (finished_at - started_at).total_seconds() * 1000.0

        metrics = None
        if isinstance(output, dict) and output.get("status") == "drained":
            metrics = output.get("metrics")
            # We don't overwrite output, we just keep it as the dictionary

        return ExecutionResult(
            success=success,
            output=output,
            exception=exception,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            metrics=metrics
        )
