import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.operational.lineage import LineageRecord

def test_lineage_record_creation():
    record = LineageRecord(
        id="lin-1",
        run_id="run-1",
        pipeline_id="etl-001",
        source_dataset="postgres.sales",
        target_dataset="s3.bucket.sales",
        rows_processed=500
    )
    assert record.rows_processed == 500
    assert record.pipeline_id == "etl-001"
