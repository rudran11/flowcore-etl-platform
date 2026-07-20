# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Metadata exceptions."""

from .base import FlowCoreError

class MetadataError(FlowCoreError):
    """Raised when there is an issue with the logical metadata structure."""
    pass
