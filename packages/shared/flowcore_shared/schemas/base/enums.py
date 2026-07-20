# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Core global enumerations."""

from enum import Enum

class ExecutionState(str, Enum):
    """Defines the state machine for an execution run or step."""
    PENDING = "PENDING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class EnvironmentType(str, Enum):
    """Defines the targeted execution environment profile."""
    DEVELOPMENT = "DEVELOPMENT"
    QA = "QA"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
