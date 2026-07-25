import pytest
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore.engine.state.manager import StateManager
from flowcore.engine.exceptions.state import StateTransitionError

def test_valid_transitions():
    assert StateManager.can_transition(ExecutionState.PENDING, ExecutionState.QUEUED)
    assert StateManager.can_transition(ExecutionState.QUEUED, ExecutionState.RUNNING)
    assert StateManager.can_transition(ExecutionState.RUNNING, ExecutionState.RETRYING)
    assert StateManager.can_transition(ExecutionState.RETRYING, ExecutionState.RUNNING)
    assert StateManager.can_transition(ExecutionState.RUNNING, ExecutionState.COMPLETED)
    assert StateManager.can_transition(ExecutionState.RUNNING, ExecutionState.FAILED)

    # Perform transition
    res = StateManager.transition(ExecutionState.PENDING, ExecutionState.QUEUED)
    assert res == ExecutionState.QUEUED

def test_terminal_states_cannot_transition():
    # COMPLETED
    assert not StateManager.can_transition(ExecutionState.COMPLETED, ExecutionState.RUNNING)
    with pytest.raises(StateTransitionError):
        StateManager.transition(ExecutionState.COMPLETED, ExecutionState.RUNNING)

    # FAILED
    assert not StateManager.can_transition(ExecutionState.FAILED, ExecutionState.RUNNING)
    with pytest.raises(StateTransitionError):
        StateManager.transition(ExecutionState.FAILED, ExecutionState.RUNNING)

    # CANCELLED
    assert not StateManager.can_transition(ExecutionState.CANCELLED, ExecutionState.RUNNING)
    with pytest.raises(StateTransitionError):
        StateManager.transition(ExecutionState.CANCELLED, ExecutionState.RUNNING)

def test_illegal_transitions():
    # Cannot jump from PENDING straight to COMPLETED
    assert not StateManager.can_transition(ExecutionState.PENDING, ExecutionState.COMPLETED)
    with pytest.raises(StateTransitionError):
        StateManager.transition(ExecutionState.PENDING, ExecutionState.COMPLETED)
