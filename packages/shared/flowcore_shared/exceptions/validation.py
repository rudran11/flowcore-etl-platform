# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Validation and parsing exceptions."""

from .base import FlowCoreError

class ValidationError(FlowCoreError):
    """Raised when metadata semantic or structural validation fails."""
    pass

class DSLParseError(ValidationError):
    """Raised specifically when the YAML/JSON pipeline definition cannot be parsed."""
    pass
