# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

class PluginError(Exception):
    """Base exception for all plugin-related errors."""
    pass

class ConfigError(PluginError):
    """Raised when the provided configuration is invalid."""
    pass

class ConnectionError(PluginError):
    """Raised when the plugin cannot connect to the external system."""
    pass

class TransientError(PluginError):
    """Raised when a temporary issue occurs (e.g., rate limits, network timeouts). Should be retried."""
    pass

class FatalError(PluginError):
    """Raised when an unrecoverable error occurs."""
    pass
