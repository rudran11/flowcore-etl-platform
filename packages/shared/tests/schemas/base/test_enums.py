from flowcore_shared.schemas.base.enums import ExecutionState, EnvironmentType

def test_execution_state_enum():
    assert ExecutionState.PENDING == "PENDING"
    assert ExecutionState.SUCCESS == "SUCCESS"
    assert ExecutionState.FAILED == "FAILED"

def test_environment_type_enum():
    assert EnvironmentType.DEVELOPMENT == "DEVELOPMENT"
    assert EnvironmentType.PRODUCTION == "PRODUCTION"
