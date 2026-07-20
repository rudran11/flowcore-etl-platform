import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.connectors.secret_reference import SecretReference

def test_secret_reference_vault():
    ref = SecretReference(vault_key="secret/data/db/password")
    assert ref.vault_key == "secret/data/db/password"

def test_secret_reference_env():
    ref = SecretReference(env_var="DB_PASSWORD")
    assert ref.env_var == "DB_PASSWORD"

def test_secret_reference_missing_both():
    with pytest.raises(ValidationError, match="must specify either"):
        SecretReference()
