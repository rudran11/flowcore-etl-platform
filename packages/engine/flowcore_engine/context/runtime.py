# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any
from datetime import datetime
import logging

class RuntimeContext(BaseModel):
    """
    Immutable execution bubble passed to Plugins.
    Provides necessary environment parameters without exposing full engine internals.
    """
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    run_id: str
    pipeline_id: str
    step_id: str
    execution_start_time: datetime
    environment: str
    working_directory: str
    temporary_directory: str
    parameters: Dict[str, Any]
    variables: Dict[str, str] = Field(default_factory=dict)
    secrets: Dict[str, str] = Field(default_factory=dict)
    logger: logging.Logger
