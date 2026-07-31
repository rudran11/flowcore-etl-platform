# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Any, Dict, Optional
from .store import AbstractStateStore

class InMemoryStateStore(AbstractStateStore):
    """
    In-memory state store for incremental synchronization testing.
    Not for production multi-node deployments.
    """
    
    def __init__(self):
        # schema: { pipeline_id: { step_id: state_dict } }
        self._states: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def get_state(self, pipeline_id: str, step_id: str) -> Optional[Dict[str, Any]]:
        pipeline_states = self._states.get(pipeline_id, {})
        return pipeline_states.get(step_id, None)

    def set_state(self, pipeline_id: str, step_id: str, state: Dict[str, Any]) -> None:
        if pipeline_id not in self._states:
            self._states[pipeline_id] = {}
        self._states[pipeline_id][step_id] = state
