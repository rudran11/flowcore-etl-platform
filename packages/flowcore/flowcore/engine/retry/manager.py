# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from flowcore.models.pipeline.retry import RetryPolicy
from flowcore_shared.schemas.base.enums import RetryStrategy
from flowcore.engine.exceptions.base import EngineError
from flowcore.engine.exceptions.plugin import FatalPluginError

class RetryManager:
    """
    Pure algorithmic calculator for retry eligibility and backoff durations.
    
    ARCHITECTURAL RULE: RetryManager must NEVER perform waiting (e.g. time.sleep).
    It only computes eligibility and delays. The ExecutionCoordinator owns scheduling
    and blocking/waiting.
    """

    @classmethod
    def should_retry(cls, error: EngineError, attempt: int, policy: RetryPolicy) -> bool:
        """
        Determines if a failure is eligible for another attempt based on error type
        and current attempt count.
        """
        if isinstance(error, FatalPluginError):
            return False
            
        if attempt >= policy.max_attempts:
            return False
            
        return True

    @classmethod
    def calculate_backoff(cls, attempt: int, policy: RetryPolicy) -> float:
        """
        Calculates the required delay duration based on the configured strategy.
        Attempt is 0-indexed (0 means the first retry).
        """
        if policy.strategy == RetryStrategy.FIXED:
            delay = policy.initial_delay_seconds
            
        elif policy.strategy == RetryStrategy.LINEAR:
            # Linear: initial, initial * 2, initial * 3...
            delay = policy.initial_delay_seconds * (attempt + 1)
            
        else: # EXPONENTIAL
            # Exponential: initial * (factor ^ attempt)
            delay = policy.initial_delay_seconds * (policy.backoff_factor ** attempt)
            
        return min(delay, policy.max_delay_seconds)
