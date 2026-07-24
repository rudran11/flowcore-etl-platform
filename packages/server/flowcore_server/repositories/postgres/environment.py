from typing import List, Optional
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from flowcore_shared.schemas.environment import Environment, EnvironmentVariable
from flowcore_server.db.environment_models import Environment as OrmEnvironment, EnvironmentVariable as OrmEnvironmentVariable, PipelineEnvironmentBinding
from flowcore_server.repositories.interfaces.environment import AbstractEnvironmentRepository
from flowcore_server.repositories.mappers.environment import map_orm_to_environment, map_environment_to_orm

class AsyncSqlAlchemyEnvironmentRepository(AbstractEnvironmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, environment: Environment) -> Environment:
        orm_env = map_environment_to_orm(environment)
        self.session.add(orm_env)
        await self.session.flush()
        
        return Environment(
            id=str(orm_env.id),
            workspace_id=str(orm_env.workspace_id),
            name=orm_env.name,
            description=orm_env.description,
            type=environment.type,
            variables=[],
            created_at=orm_env.created_at,
            updated_at=orm_env.updated_at
        )

    async def get(self, environment_id: str) -> Optional[Environment]:
        stmt = select(OrmEnvironment).options(selectinload(OrmEnvironment.variables)).where(OrmEnvironment.id == uuid.UUID(environment_id))
        result = await self.session.execute(stmt)
        orm_env = result.scalars().first()
        if orm_env:
            return map_orm_to_environment(orm_env)
        return None

    async def update(self, environment: Environment) -> Environment:
        stmt = select(OrmEnvironment).options(selectinload(OrmEnvironment.variables)).where(OrmEnvironment.id == uuid.UUID(environment.id))
        result = await self.session.execute(stmt)
        orm_env = result.scalars().first()
        if orm_env:
            orm_env.name = environment.name
            orm_env.description = environment.description
            orm_env.type = environment.type.value
            await self.session.flush()
            return map_orm_to_environment(orm_env)
        raise ValueError("Environment not found")

    async def delete(self, environment_id: str) -> None:
        stmt = delete(OrmEnvironment).where(OrmEnvironment.id == uuid.UUID(environment_id))
        await self.session.execute(stmt)
        await self.session.flush()

    async def list_by_workspace(self, workspace_id: str) -> List[Environment]:
        stmt = select(OrmEnvironment).options(selectinload(OrmEnvironment.variables)).where(OrmEnvironment.workspace_id == uuid.UUID(workspace_id)).order_by(OrmEnvironment.name)
        result = await self.session.execute(stmt)
        return [map_orm_to_environment(env) for env in result.scalars().all()]

    async def add_variable(self, environment_id: str, variable: EnvironmentVariable, encrypted_value: Optional[str] = None) -> None:
        orm_var = OrmEnvironmentVariable(
            id=uuid.UUID(variable.id),
            environment_id=uuid.UUID(environment_id),
            key=variable.key,
            value=variable.value if not variable.is_secret else None,
            is_secret=variable.is_secret,
            encrypted_value=encrypted_value if variable.is_secret else None
        )
        self.session.add(orm_var)
        await self.session.flush()

    async def update_variable(self, environment_id: str, variable: EnvironmentVariable, encrypted_value: Optional[str] = None) -> None:
        stmt = select(OrmEnvironmentVariable).where(OrmEnvironmentVariable.id == uuid.UUID(variable.id)).where(OrmEnvironmentVariable.environment_id == uuid.UUID(environment_id))
        result = await self.session.execute(stmt)
        orm_var = result.scalars().first()
        if orm_var:
            orm_var.key = variable.key
            orm_var.is_secret = variable.is_secret
            orm_var.value = variable.value if not variable.is_secret else None
            orm_var.encrypted_value = encrypted_value if variable.is_secret else None
            await self.session.flush()
        else:
            raise ValueError("Variable not found")

    async def delete_variable(self, environment_id: str, variable_id: str) -> None:
        stmt = delete(OrmEnvironmentVariable).where(OrmEnvironmentVariable.id == uuid.UUID(variable_id)).where(OrmEnvironmentVariable.environment_id == uuid.UUID(environment_id))
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_raw_variables(self, environment_id: str) -> List[OrmEnvironmentVariable]:
        stmt = select(OrmEnvironmentVariable).where(OrmEnvironmentVariable.environment_id == uuid.UUID(environment_id))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def bind_pipeline(self, pipeline_id: str, environment_id: str) -> None:
        binding = PipelineEnvironmentBinding(pipeline_id=uuid.UUID(pipeline_id), environment_id=uuid.UUID(environment_id))
        self.session.add(binding)
        await self.session.flush()

    async def unbind_pipeline(self, pipeline_id: str, environment_id: str) -> None:
        stmt = delete(PipelineEnvironmentBinding).where(PipelineEnvironmentBinding.pipeline_id == uuid.UUID(pipeline_id)).where(PipelineEnvironmentBinding.environment_id == uuid.UUID(environment_id))
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_bound_environments(self, pipeline_id: str) -> List[Environment]:
        stmt = select(OrmEnvironment).join(PipelineEnvironmentBinding, OrmEnvironment.id == PipelineEnvironmentBinding.environment_id).where(PipelineEnvironmentBinding.pipeline_id == uuid.UUID(pipeline_id))
        result = await self.session.execute(stmt)
        return [map_orm_to_environment(env) for env in result.scalars().all()]
