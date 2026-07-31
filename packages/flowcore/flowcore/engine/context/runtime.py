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
    
    # Internal context for pipelines
    message_stream: Any = Field(None, description="Stream of messages from upstream plugin")
    catalog: Any = Field(None, description="Catalog for discovery/sync")
    state: Dict[str, Any] = Field(default_factory=dict, description="Incremental state dictionary")
    
    # Lineage tracking
    input_datasets: list = Field(default_factory=list, description="List of input datasets reported by the plugin")
    output_datasets: list = Field(default_factory=list, description="List of output datasets reported by the plugin")

    def report_input_dataset(self, name: str, dataset_type: str, columns: list = None):
        """Plugin authors can call this to report a dataset read"""
        self.input_datasets.append({
            "name": name,
            "type": dataset_type,
            "columns": columns or []
        })

    def report_output_dataset(self, name: str, dataset_type: str, columns: list = None):
        """Plugin authors can call this to report a dataset write"""
        self.output_datasets.append({
            "name": name,
            "type": dataset_type,
            "columns": columns or []
        })
