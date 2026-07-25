# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_engine.exceptions.state import StateTransitionError

class StateManager:
    """
    Pure state machine validator for the execution lifecycle.
    """
    
    # Define valid transitions: { current_state: [allowed target states] }
    TRANSITIONS = {
        ExecutionState.PENDING: [ExecutionState.QUEUED, ExecutionState.CANCELLED],
        ExecutionState.QUEUED: [ExecutionState.RUNNING, ExecutionState.CANCELLED],
        ExecutionState.RUNNING: [
            ExecutionState.COMPLETED, 
            ExecutionState.FAILED, 
            ExecutionState.CANCELLED, 
            ExecutionState.RETRYING
        ],
        ExecutionState.RETRYING: [ExecutionState.RUNNING, ExecutionState.FAILED, ExecutionState.CANCELLED],
        ExecutionState.FAILED: [],
        ExecutionState.CANCELLED: [],
        ExecutionState.COMPLETED: [],
    }

    @classmethod
    def can_transition(cls, current_state: ExecutionState, target_state: ExecutionState) -> bool:
        """Returns True if the transition is allowed."""
        allowed_targets = cls.TRANSITIONS.get(current_state, [])
        return target_state in allowed_targets

    @classmethod
    def transition(cls, current_state: ExecutionState, target_state: ExecutionState) -> ExecutionState:
        """
        Validates and returns the target state if legal.
        Raises StateTransitionError if illegal.
        """
        if not cls.can_transition(current_state, target_state):
            raise StateTransitionError(
                f"Illegal state transition from {current_state.value} to {target_state.value}"
            )
        return target_state
