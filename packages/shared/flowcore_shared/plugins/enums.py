# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from enum import Enum

class PluginType(str, Enum):
    """Types of plugins supported by FlowCore."""
    CONNECTOR = "CONNECTOR"
    TRANSFORMER = "TRANSFORMER"
