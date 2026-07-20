import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.pipeline.retry import RetryPolicy
from flowcore_shared.schemas.base.enums import RetryStrategy

def test_retry_policy_defaults():
    policy = RetryPolicy()
    assert policy.max_attempts == 3
    assert policy.initial_delay_seconds == 1.0
    assert policy.backoff_factor == 2.0
    assert policy.max_delay_seconds == 60.0
    assert policy.strategy == RetryStrategy.EXPONENTIAL
    assert policy.enable_jitter is False

def test_retry_policy_custom():
    policy = RetryPolicy(
        max_attempts=5,
        strategy=RetryStrategy.FIXED,
        enable_jitter=True
    )
    assert policy.max_attempts == 5
    assert policy.strategy == RetryStrategy.FIXED
    assert policy.enable_jitter is True
