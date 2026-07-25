# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from enum import Enum

class PluginLifecycleState(str, Enum):
    """Diagnostic lifecycle states for a plugin during the manager's loading phase."""
    DISCOVERED = "DISCOVERED"
    LOADED = "LOADED"
    VALIDATED = "VALIDATED"
    READY = "READY"
