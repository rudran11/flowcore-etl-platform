import os
import uuid
import base64
from typing import List, Dict, Optional
from cryptography.fernet import Fernet


from flowcore_shared.schemas.environment import (
    Environment, EnvironmentVariable, EnvironmentVariableCreate, EnvironmentVariableUpdate, EnvironmentType
)
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.config.settings import settings

class EnvironmentService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        
        # Load master key for Fernet. In production, this should come from FLOWCORE_SECRET_KEY
        secret_key_b64 = settings.secret_key or os.environ.get("FLOWCORE_SECRET_KEY")
        if not secret_key_b64:
            # For development MVP, generate a temporary one if missing, but print a warning.
            # (Note: keys encrypted with a temporary key will be unreadable after restart)
            import logging
            logger = logging.getLogger("flowcore")
            logger.warning("FLOWCORE_SECRET_KEY not set! Using an ephemeral key. Secrets will be lost on restart.")
            secret_key_b64 = Fernet.generate_key().decode("utf-8")
        
        self.fernet = Fernet(secret_key_b64.encode("utf-8"))

    def encrypt(self, plain_text: str) -> str:
        return self.fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        return self.fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")

    async def get_environment_context(self, environment_id: str) -> Dict[str, Dict[str, str]]:
        """
        Resolves the variables and secrets for the given environment.
        Returns a dict with 'variables' and 'secrets'.
        """
        async with self.uow:
            env = await self.uow.environments.get(environment_id)
            if not env:
                raise ValueError("Environment not found")
                
            raw_vars = await self.uow.environments.get_raw_variables(environment_id)
            
            variables = {}
            secrets = {}
            
            for v in raw_vars:
                if v.is_secret:
                    if v.encrypted_value:
                        try:
                            secrets[v.key] = self.decrypt(v.encrypted_value)
                        except Exception:
                            secrets[v.key] = "<decryption-failed>"
                else:
                    variables[v.key] = v.value or ""
                    
            return {
                "variables": variables,
                "secrets": secrets,
                "environment_type": env.type.value
            }

    async def add_variable(self, environment_id: str, data: EnvironmentVariableCreate) -> None:
        async with self.uow:
            var_id = str(uuid.uuid4())
            var = EnvironmentVariable(
                id=var_id,
                key=data.key,
                value=data.value if not data.is_secret else "********",
                is_secret=data.is_secret
            )
            
            encrypted_val = self.encrypt(data.value) if data.is_secret else None
            
            await self.uow.environments.add_variable(environment_id, var, encrypted_value=encrypted_val)
            await self.uow.commit()

    async def update_variable(self, environment_id: str, variable_id: str, data: EnvironmentVariableUpdate) -> None:
        async with self.uow:
            raw_vars = await self.uow.environments.get_raw_variables(environment_id)
            var_orm = next((v for v in raw_vars if str(v.id) == variable_id), None)
            if not var_orm:
                raise ValueError("Variable not found")
                
            var = EnvironmentVariable(
                id=variable_id,
                key=data.key if data.key is not None else var_orm.key,
                value="********",
                is_secret=data.is_secret if data.is_secret is not None else var_orm.is_secret
            )
            
            # If secret and value is updated, re-encrypt
            encrypted_val = var_orm.encrypted_value
            if var.is_secret:
                if data.value is not None:
                    encrypted_val = self.encrypt(data.value)
                    var.value = "********"
            else:
                if data.value is not None:
                    var.value = data.value
                else:
                    var.value = var_orm.value
                    
            await self.uow.environments.update_variable(environment_id, var, encrypted_value=encrypted_val)
            await self.uow.commit()

    async def clone_environment(self, source_id: str, new_name: str, new_type: EnvironmentType) -> Environment:
        async with self.uow:
            source_env = await self.uow.environments.get(source_id)
            if not source_env:
                raise ValueError("Source environment not found")
                
            new_env_id = str(uuid.uuid4())
            new_env = Environment(
                id=new_env_id,
                workspace_id=source_env.workspace_id,
                name=new_name,
                description=f"Cloned from {source_env.name}",
                type=new_type,
                variables=[]
            )
            created_env = await self.uow.environments.create(new_env)
            
            raw_vars = await self.uow.environments.get_raw_variables(source_id)
            for v in raw_vars:
                new_var = EnvironmentVariable(
                    id=str(uuid.uuid4()),
                    key=v.key,
                    value=v.value if not v.is_secret else "********",
                    is_secret=v.is_secret
                )
                await self.uow.environments.add_variable(new_env_id, new_var, encrypted_value=v.encrypted_value)
                
            await self.uow.commit()
            return await self.uow.environments.get(new_env_id)

    async def import_env_file(self, environment_id: str, content: str) -> None:
        """Parses a .env string and adds variables."""
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                await self.add_variable(environment_id, EnvironmentVariableCreate(
                    key=k.strip(),
                    value=v.strip(),
                    is_secret=False
                ))

    async def export_env_file(self, environment_id: str) -> str:
        """Exports environment to .env format (excluding secrets)."""
        async with self.uow:
            env = await self.uow.environments.get(environment_id)
            if not env:
                raise ValueError("Environment not found")
                
            lines = [f"# Exported from {env.name} ({env.type.value})"]
            for v in env.variables:
                if not v.is_secret:
                    lines.append(f"{v.key}={v.value}")
            return "\\n".join(lines)
