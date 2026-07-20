# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Configuration exceptions."""

from .base import FlowCoreError

class ConfigurationError(FlowCoreError):
    """Raised when environment variables or profile configurations are invalid."""
    pass
