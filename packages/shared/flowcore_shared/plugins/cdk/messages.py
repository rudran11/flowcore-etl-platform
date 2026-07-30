# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import Field
from flowcore_shared.schemas.base.models import FlowCoreBaseModel

class MessageType(str, Enum):
    RECORD = "RECORD"
    STATE = "STATE"
    SCHEMA = "SCHEMA"
    LOG = "LOG"

class RecordMessage(FlowCoreBaseModel):
    stream: str = Field(..., description="Name of the stream this record belongs to.")
    data: Dict[str, Any] = Field(..., description="The actual record data.")
    time_extracted: datetime = Field(default_factory=datetime.utcnow, description="When the record was extracted.")

class StateMessage(FlowCoreBaseModel):
    stream: Optional[str] = Field(None, description="Stream this state applies to, or None for global state.")
    state_data: Dict[str, Any] = Field(..., description="The state payload.")

class SchemaMessage(FlowCoreBaseModel):
    stream: str = Field(..., description="Name of the stream.")
    schema_json: Dict[str, Any] = Field(..., description="JSON schema describing the stream.")

class LogMessage(FlowCoreBaseModel):
    level: str = Field(..., description="Log level (INFO, WARN, ERROR, DEBUG).")
    message: str = Field(..., description="The log message.")

class FlowCoreMessage(FlowCoreBaseModel):
    type: MessageType = Field(..., description="The type of this message.")
    record: Optional[RecordMessage] = Field(None, description="Record payload if type == RECORD")
    state: Optional[StateMessage] = Field(None, description="State payload if type == STATE")
    schema_info: Optional[SchemaMessage] = Field(None, description="Schema payload if type == SCHEMA")
    log: Optional[LogMessage] = Field(None, description="Log payload if type == LOG")
