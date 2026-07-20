# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Lineage record schema."""

from pydantic import Field
from flowcore_shared.schemas.base.models import MetadataEntity

class LineageRecord(MetadataEntity):
    """
    Tracks data movement from a source to a target during an execution run.
    """
    run_id: str = Field(..., description="The ID of the ExecutionRun that generated this lineage.")
    pipeline_id: str = Field(..., description="The ID of the Pipeline.")
    source_dataset: str = Field(..., description="The origin dataset identifier (e.g., source table).")
    target_dataset: str = Field(..., description="The destination dataset identifier (e.g., target table).")
    rows_processed: int = Field(0, description="The number of rows/records successfully processed.")
