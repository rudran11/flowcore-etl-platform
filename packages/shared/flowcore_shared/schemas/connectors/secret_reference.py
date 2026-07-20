# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Secret reference metadata schema."""

from typing import Optional
from pydantic import Field, model_validator
from flowcore_shared.schemas.base.models import FlowCoreBaseModel
from flowcore_shared.exceptions.validation import ValidationError

class SecretReference(FlowCoreBaseModel):
    """
    A secure reference to a secret stored externally (e.g., Vault or Environment).
    Strictly forbids plaintext passwords.
    """
    vault_key: Optional[str] = Field(None, description="Path or key in a secure secrets vault.")
    env_var: Optional[str] = Field(None, description="Name of the environment variable containing the secret.")

    @model_validator(mode="after")
    def validate_reference_provided(self) -> "SecretReference":
        if not self.vault_key and not self.env_var:
            raise ValueError("A SecretReference must specify either a 'vault_key' or an 'env_var'.")
        return self
