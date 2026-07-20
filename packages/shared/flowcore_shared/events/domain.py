# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typing import Optional
from .base import DomainEvent

class PipelineExecutionStarted(DomainEvent):
    """Event emitted when a pipeline execution transitions to started/pending."""
    event_type: str = "PipelineExecutionStarted"
    
    run_id: str
    pipeline_id: str
    pipeline_version_id: str

class PipelineExecutionCompleted(DomainEvent):
    """Event emitted when a pipeline execution completes successfully."""
    event_type: str = "PipelineExecutionCompleted"
    
    run_id: str
    pipeline_id: str
    pipeline_version_id: str

class PipelineExecutionFailed(DomainEvent):
    """Event emitted when a pipeline execution fails."""
    event_type: str = "PipelineExecutionFailed"
    
    run_id: str
    pipeline_id: str
    pipeline_version_id: str
    error_message: Optional[str] = None

class RunCancelled(DomainEvent):
    """Event emitted when a pipeline execution is cancelled by a user or system."""
    event_type: str = "RunCancelled"
    
    run_id: str
    pipeline_id: str
    pipeline_version_id: str
