import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.operational.health import HealthRecord

def test_health_record_creation():
    record = HealthRecord(
        id="health-1",
        component_id="engine-worker-1",
        status="HEALTHY",
        message="Running normally"
    )
    assert record.status == "HEALTHY"
    assert record.component_id == "engine-worker-1"
