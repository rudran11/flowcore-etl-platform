# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from datetime import datetime
from typing import Optional
from pydantic import Field, BaseModel
from flowcore_shared.schemas.base.models import MetadataEntity

class WebhookTriggerBase(MetadataEntity):
    workspace_id: str = Field(..., description="The workspace this webhook belongs to.")
    pipeline_id: str = Field(..., description="The pipeline this webhook triggers.")
    name: str = Field(..., description="A friendly name for this webhook.")
    is_active: bool = Field(default=True, description="Whether this webhook is currently active.")

class WebhookTriggerCreate(WebhookTriggerBase):
    pass

class WebhookTriggerUpdate(BaseModel):
    name: Optional[str] = Field(None, description="A friendly name for this webhook.")
    is_active: Optional[bool] = Field(None, description="Whether this webhook is currently active.")
    regenerate_secret: bool = Field(default=False, description="Whether to regenerate the HMAC secret.")

class WebhookTriggerResponse(WebhookTriggerBase):
    id: str = Field(..., description="The unique identifier for this webhook.")
    secret_key: Optional[str] = Field(None, description="The HMAC secret key (only returned on creation/regeneration).")

class WebhookTriggerInDB(WebhookTriggerBase):
    id: str = Field(..., description="The unique identifier for this webhook.")
    secret_key_hash: str = Field(..., description="The hashed version of the secret key for validation.")
