from flowcore_shared.schemas.base.enums import ExecutionState, EnvironmentType, RetryStrategy

def test_execution_state_enum():
    assert ExecutionState.PENDING == "PENDING"
    assert ExecutionState.COMPLETED == "COMPLETED"
    assert ExecutionState.FAILED == "FAILED"

def test_environment_type_enum():
    assert EnvironmentType.DEVELOPMENT == "DEVELOPMENT"
    assert EnvironmentType.PRODUCTION == "PRODUCTION"

def test_retry_strategy_enum():
    assert RetryStrategy.FIXED == "FIXED"
    assert RetryStrategy.LINEAR == "LINEAR"
    assert RetryStrategy.EXPONENTIAL == "EXPONENTIAL"
