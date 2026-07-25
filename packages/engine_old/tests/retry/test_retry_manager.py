import pytest
from flowcore.models.pipeline.retry import RetryPolicy
from flowcore_shared.schemas.base.enums import RetryStrategy
from flowcore_engine.retry.manager import RetryManager
from flowcore_engine.exceptions.base import EngineError
from flowcore_engine.exceptions.plugin import RecoverablePluginError, FatalPluginError

def test_should_retry_recoverable():
    policy = RetryPolicy(max_attempts=3)
    error = RecoverablePluginError("Timeout")
    
    assert RetryManager.should_retry(error, attempt=0, policy=policy)
    assert RetryManager.should_retry(error, attempt=1, policy=policy)
    assert RetryManager.should_retry(error, attempt=2, policy=policy)
    assert not RetryManager.should_retry(error, attempt=3, policy=policy)

def test_should_retry_fatal():
    policy = RetryPolicy(max_attempts=5)
    error = FatalPluginError("Syntax error")
    
    # Fatal error should bypass max_attempts and immediately reject retry
    assert not RetryManager.should_retry(error, attempt=0, policy=policy)

def test_calculate_backoff_fixed():
    policy = RetryPolicy(strategy=RetryStrategy.FIXED, initial_delay_seconds=2.0)
    
    assert RetryManager.calculate_backoff(attempt=0, policy=policy) == 2.0
    assert RetryManager.calculate_backoff(attempt=1, policy=policy) == 2.0
    assert RetryManager.calculate_backoff(attempt=5, policy=policy) == 2.0

def test_calculate_backoff_linear():
    policy = RetryPolicy(strategy=RetryStrategy.LINEAR, initial_delay_seconds=2.0)
    
    # attempt 0 -> 2.0 * 1 = 2.0
    assert RetryManager.calculate_backoff(attempt=0, policy=policy) == 2.0
    # attempt 1 -> 2.0 * 2 = 4.0
    assert RetryManager.calculate_backoff(attempt=1, policy=policy) == 4.0
    # attempt 2 -> 2.0 * 3 = 6.0
    assert RetryManager.calculate_backoff(attempt=2, policy=policy) == 6.0

def test_calculate_backoff_exponential():
    policy = RetryPolicy(
        strategy=RetryStrategy.EXPONENTIAL, 
        initial_delay_seconds=1.0,
        backoff_factor=2.0,
        max_delay_seconds=60.0
    )
    
    # attempt 0 -> 1.0 * (2^0) = 1.0
    assert RetryManager.calculate_backoff(attempt=0, policy=policy) == 1.0
    # attempt 1 -> 1.0 * (2^1) = 2.0
    assert RetryManager.calculate_backoff(attempt=1, policy=policy) == 2.0
    # attempt 2 -> 1.0 * (2^2) = 4.0
    assert RetryManager.calculate_backoff(attempt=2, policy=policy) == 4.0
    # attempt 3 -> 1.0 * (2^3) = 8.0
    assert RetryManager.calculate_backoff(attempt=3, policy=policy) == 8.0

def test_calculate_backoff_max_delay():
    policy = RetryPolicy(
        strategy=RetryStrategy.EXPONENTIAL, 
        initial_delay_seconds=10.0,
        backoff_factor=10.0,
        max_delay_seconds=50.0
    )
    
    # attempt 0 -> 10.0
    assert RetryManager.calculate_backoff(attempt=0, policy=policy) == 10.0
    # attempt 1 -> 100.0, capped to 50.0
    assert RetryManager.calculate_backoff(attempt=1, policy=policy) == 50.0
