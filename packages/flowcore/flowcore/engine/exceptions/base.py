# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from flowcore_shared.exceptions.base import FlowCoreError
from flowcore_shared.schemas.base.enums import RetryStrategy

class EngineError(FlowCoreError):
    """Base exception for all execution engine errors."""
    is_retryable: bool = False
    default_strategy: RetryStrategy = RetryStrategy.FIXED
    default_delay: int = 5
    error_category: str = "EngineError"

class NetworkTimeoutError(EngineError):
    """Upstream/Downstream API timeout."""
    is_retryable = True
    default_strategy = RetryStrategy.EXPONENTIAL
    default_delay = 5
    error_category = "NetworkTimeoutError"

class RateLimitError(EngineError):
    """HTTP 429 from Source."""
    is_retryable = True
    default_strategy = RetryStrategy.LINEAR
    default_delay = 10
    error_category = "RateLimitError"

class DataSchemaMismatch(EngineError):
    """Incoming data violates schema."""
    is_retryable = False
    error_category = "DataSchemaMismatch"

class AuthenticationError(EngineError):
    """Invalid credentials for source/dest."""
    is_retryable = False
    error_category = "AuthenticationError"

class InternalEngineError(EngineError):
    """OOM, Memory Limits, DB disconnect."""
    is_retryable = True
    default_strategy = RetryStrategy.FIXED
    default_delay = 5
    error_category = "InternalEngineError"
