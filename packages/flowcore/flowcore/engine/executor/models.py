# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from dataclasses import dataclass
from typing import Any, Optional, Dict
from datetime import datetime
from enum import Enum

class ExecutorType(str, Enum):
    """
    Defines the type of execution backend.
    Future extensions will support PROCESS, DOCKER, and KUBERNETES.
    """
    LOCAL = "LOCAL"
    THREAD = "THREAD"

@dataclass
class ExecutionResult:
    """
    Standardized result for any task executed by an AbstractExecutor.
    """
    success: bool
    output: Any
    exception: Optional[Exception]
    started_at: datetime
    finished_at: datetime
    duration_ms: float
    metrics: Optional[Dict[str, Any]] = None
