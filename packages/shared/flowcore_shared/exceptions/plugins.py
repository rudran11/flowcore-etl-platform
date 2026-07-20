# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Plugin and connector exceptions."""

from .base import FlowCoreError

class PluginError(FlowCoreError):
    """Raised when a plugin fails to initialize or crashes."""
    pass

class ConnectorError(PluginError):
    """Raised when an I/O connector fails to establish connection or transact."""
    pass
