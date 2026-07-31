# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AbstractStateStore(ABC):
    """
    Abstract interface for persisting and restoring incremental pipeline state.
    Allows injecting different backends (DB, File, Memory) without modifying connectors.
    """
    
    @abstractmethod
    def get_state(self, pipeline_id: str, step_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest committed state for a specific connector.
        Returns None if no previous state exists.
        """
        pass
        
    @abstractmethod
    def set_state(self, pipeline_id: str, step_id: str, state: Dict[str, Any]) -> None:
        """
        Persists a new incremental state checkpoint.
        """
        pass
