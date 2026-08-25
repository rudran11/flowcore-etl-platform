# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any
from datetime import datetime
import logging
import threading

class PreviewExecutionContext(BaseModel):
    """
    Context object to signal bounded preview constraints.
    """
    is_preview: bool = Field(default=False, description="True if this is a preview execution.")
    record_limit: int = Field(default=50, description="The maximum number of records to process for UI display.")
    execution_limit: int = Field(default=5000, description="The maximum number of records to execute before cancelling upstream.")
    
    # Internal flag used by engine to gracefully signal cancellation
    # We use a primitive dict since threading.Event cannot be easily validated by Pydantic's frozen model without custom validators.
    # Alternatively we can just use arbitrary types.
    model_config = ConfigDict(arbitrary_types_allowed=True)
    cancellation_event: threading.Event = Field(default_factory=threading.Event, description="Event to signal graceful termination.")

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
    message_streams: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of message streams from multiple upstreams (for Joins)")
    catalog: Any = Field(None, description="Catalog for discovery/sync")
    state: Dict[str, Any] = Field(default_factory=dict, description="Incremental state dictionary")
    
    # Lineage tracking
    input_datasets: list = Field(default_factory=list, description="List of input datasets reported by the plugin")
    output_datasets: list = Field(default_factory=list, description="List of output datasets reported by the plugin")
    
    # Preview context
    preview_context: PreviewExecutionContext = Field(default_factory=PreviewExecutionContext, description="Preview constraints")
    
    # Global cancellation event
    cancellation_event: threading.Event = Field(default_factory=threading.Event, description="Event to signal graceful cancellation of the run")

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
