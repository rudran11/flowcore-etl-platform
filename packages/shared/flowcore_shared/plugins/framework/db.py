# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import queue
import time
from typing import Any, Callable, Generic, TypeVar
from contextlib import contextmanager

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

T = TypeVar('T')

class ConnectionPool(Generic[T]):
    """
    A generic connection pool for database connectors.
    """
    def __init__(self, create_fn: Callable[[], T], max_connections: int = 5, ping_fn: Callable[[T], bool] = None):
        self.create_fn = create_fn
        self.ping_fn = ping_fn
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_count = 0

    def get_connection(self) -> T:
        try:
            conn = self.pool.get(block=False)
            if self.ping_fn and not self.ping_fn(conn):
                # Connection is dead, create a new one
                return self.create_fn()
            return conn
        except queue.Empty:
            if self.active_count < self.max_connections:
                self.active_count += 1
                return self.create_fn()
            else:
                # Wait for a connection to be released
                return self.pool.get(block=True, timeout=30.0)

    def release(self, conn: T):
        try:
            self.pool.put(conn, block=False)
        except queue.Full:
            # Should not happen if logic is correct, but just in case
            pass

@contextmanager
def acquire_connection(pool: ConnectionPool[T]):
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.release(conn)

# Re-usable retry decorator for transient DB errors
def retry_on_transient(exceptions: tuple):
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(exceptions),
        reraise=True
    )
