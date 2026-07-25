# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from .base import EngineError

class StateTransitionError(EngineError):
    """Raised when an illegal state transition is attempted."""
    pass
