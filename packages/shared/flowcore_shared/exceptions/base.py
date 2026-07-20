# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Base exception for FlowCore platform."""

class FlowCoreError(Exception):
    """
    The foundational exception for the FlowCore platform.
    All custom exceptions must inherit from this class.
    """
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
