# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from dataclasses import dataclass
from typing import Optional
from flowcore_engine.context.runtime import RuntimeContext

@dataclass(frozen=True)
class ExecutionTask:
    """
    Immutable representation of an executable unit of work.
    Constructed by the ExecutionCoordinator and consumed by the EngineRunner.
    """
    step_id: str
    plugin_id: str
    runtime_context: RuntimeContext
    retry_attempt: int
    timeout_seconds: Optional[int]
