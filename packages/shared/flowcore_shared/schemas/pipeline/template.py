# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Template metadata schema."""

from typing import Dict, Any
from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class Template(MetadataEntity):
    """
    Represents a reusable blueprint for a pipeline or step.
    """
    name: str = Field(..., description="Name of the template.")
    template_type: str = Field(..., description="Type of the template (e.g., 'PIPELINE', 'STEP').")
    default_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default parameters for template instantiation."
    )
    body: Dict[str, Any] = Field(
        ...,
        description="The raw payload structure to be parameterized."
    )
