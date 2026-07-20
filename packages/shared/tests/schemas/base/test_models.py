import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.base.models import MetadataEntity

def test_metadata_entity_creation():
    entity = MetadataEntity(id="test-123")
    assert entity.id == "test-123"
    assert entity.created_at is not None
    assert entity.updated_at is None

def test_metadata_entity_missing_id():
    with pytest.raises(ValidationError):
        MetadataEntity()

def test_metadata_entity_is_frozen():
    entity = MetadataEntity(id="test-123")
    with pytest.raises(ValidationError):
        entity.id = "new-id"
