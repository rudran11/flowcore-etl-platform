# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from .base import EngineError

class RecoverablePluginError(EngineError):
    """Transient failure that should be retried by the RetryManager."""
    pass

class FatalPluginError(EngineError):
    """Unrecoverable failure that should bypass retries entirely."""
    pass

class PluginLoadError(EngineError):
    """Error encountered during plugin discovery, loading, or validation."""
    pass
