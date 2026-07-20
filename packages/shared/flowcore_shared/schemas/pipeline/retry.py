# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional
from flowcore_shared.schemas.base.models import FlowCoreBaseModel
from flowcore_shared.schemas.base.enums import RetryStrategy

class RetryPolicy(FlowCoreBaseModel):
    """Configuration for step-level retry behavior."""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    backoff_factor: float = 2.0
    max_delay_seconds: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    enable_jitter: bool = False  # Reserved for future milestone to prevent thundering herds
