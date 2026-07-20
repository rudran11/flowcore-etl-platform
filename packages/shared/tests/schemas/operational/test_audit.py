import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.operational.audit import AuditLog

def test_audit_log_creation():
    log = AuditLog(
        id="audit-1",
        actor_id="user_john",
        action_type="CREATE_PIPELINE",
        resource_id="etl-001",
        resource_type="PIPELINE"
    )
    assert log.actor_id == "user_john"
    assert log.action_type == "CREATE_PIPELINE"
    assert log.resource_id == "etl-001"

def test_audit_log_missing_field():
    with pytest.raises(ValidationError):
        AuditLog(id="audit-1", actor_id="user_john")
