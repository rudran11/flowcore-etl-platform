from flowcore_shared.schemas.environment import Environment, EnvironmentVariable, EnvironmentType
from flowcore_server.db.environment_models import Environment as OrmEnvironment, EnvironmentVariable as OrmEnvironmentVariable
import uuid

def map_orm_to_environment(orm_obj: OrmEnvironment) -> Environment:
    variables = []
    if orm_obj.variables:
        for v in orm_obj.variables:
            variables.append(EnvironmentVariable(
                id=str(v.id),
                key=v.key,
                value=v.value if not v.is_secret else "********",
                is_secret=v.is_secret
            ))

    return Environment(
        id=str(orm_obj.id),
        workspace_id=str(orm_obj.workspace_id),
        name=orm_obj.name,
        description=orm_obj.description,
        type=EnvironmentType(orm_obj.type),
        variables=variables,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )

def map_environment_to_orm(domain_obj: Environment) -> OrmEnvironment:
    return OrmEnvironment(
        id=uuid.UUID(domain_obj.id),
        workspace_id=uuid.UUID(domain_obj.workspace_id),
        name=domain_obj.name,
        description=domain_obj.description,
        type=domain_obj.type.value,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at
    )
