# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Callable, Any
from concurrent.futures import Future
from .base import AbstractExecutor
from .models import ExecutionResult

class LocalExecutor(AbstractExecutor):
    """
    Executes tasks synchronously in the current thread.
    Useful for testing and single-task isolated environments.
    """

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[ExecutionResult]:
        """
        Executes the function immediately and returns a resolved Future.
        """
        result = self._execute_wrapped(fn, *args, **kwargs)
        future: Future[ExecutionResult] = Future()
        future.set_result(result)
        return future

    def shutdown(self, wait: bool = True) -> None:
        """No-op for the local executor."""
        pass
