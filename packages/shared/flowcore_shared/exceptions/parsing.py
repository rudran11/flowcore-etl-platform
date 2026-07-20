# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Parsing specific exceptions."""

from flowcore_shared.exceptions.base import FlowCoreError

class DSLParseError(FlowCoreError):
    """Raised when DSL parsing fails to map or validate against core schemas."""
    pass
