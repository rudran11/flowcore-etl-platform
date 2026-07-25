# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Callable, Any, Optional
from concurrent.futures import Future, ThreadPoolExecutor as PyThreadPoolExecutor
from .base import AbstractExecutor
from .models import ExecutionResult

class ThreadExecutor(AbstractExecutor):
    """
    Executes tasks asynchronously using a ThreadPoolExecutor.
    Suitable for I/O bound workloads.
    """

    def __init__(self, max_workers: Optional[int] = None) -> None:
        """
        Initializes the ThreadExecutor.
        Allows explicit configuration of max_workers.
        """
        self._pool = PyThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[ExecutionResult]:
        """
        Submits the function to the thread pool, returning a Future for the ExecutionResult.
        """
        return self._pool.submit(self._execute_wrapped, fn, *args, **kwargs)

    def shutdown(self, wait: bool = True) -> None:
        """
        Shuts down the underlying thread pool.
        """
        self._pool.shutdown(wait=wait)
