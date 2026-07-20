# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from flowcore_shared.exceptions.base import FlowCoreError

class EngineError(FlowCoreError):
    """Base exception for all execution engine errors."""
    pass

class StateTransitionError(EngineError):
    """Raised when an illegal state transition is attempted."""
    pass
