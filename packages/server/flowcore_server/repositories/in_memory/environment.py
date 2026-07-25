from typing import List, Optional
from flowcore_server.repositories.interfaces.environment import AbstractEnvironmentRepository
from flowcore_shared.schemas.environment import Environment, EnvironmentVariable
from flowcore_server.db.environment_models import EnvironmentVariable as OrmEnvironmentVariable

class InMemoryEnvironmentRepository(AbstractEnvironmentRepository):
    def __init__(self):
        self.environments: dict[str, Environment] = {}
        self.variables: dict[str, list] = {}  # env_id -> list of OrmEnvironmentVariable mock dicts
        self.bindings: dict[str, set] = {} # pipeline_id -> set of env_ids

    async def create(self, environment: Environment) -> Environment:
        self.environments[environment.id] = environment
        self.variables[environment.id] = []
        return environment

    async def get(self, environment_id: str) -> Optional[Environment]:
        return self.environments.get(environment_id)

    async def update(self, environment: Environment) -> Environment:
        self.environments[environment.id] = environment
        return environment

    async def delete(self, environment_id: str) -> None:
        if environment_id in self.environments:
            del self.environments[environment_id]
        if environment_id in self.variables:
            del self.variables[environment_id]

    async def list_by_workspace(self, workspace_id: str) -> List[Environment]:
        return [env for env in self.environments.values() if env.workspace_id == workspace_id]

    async def add_variable(self, environment_id: str, variable: EnvironmentVariable, encrypted_value: Optional[str] = None) -> None:
        if environment_id not in self.variables:
            self.variables[environment_id] = []
        
        mock_orm_var = OrmEnvironmentVariable(
            id=variable.id,
            environment_id=environment_id,
            key=variable.key,
            is_secret=variable.is_secret,
            encrypted_value=encrypted_value,
            value=variable.value if not variable.is_secret else None
        )
        self.variables[environment_id].append(mock_orm_var)

    async def update_variable(self, environment_id: str, variable: EnvironmentVariable, encrypted_value: Optional[str] = None) -> None:
        if environment_id not in self.variables:
            return
            
        for idx, var in enumerate(self.variables[environment_id]):
            if var.id == variable.id:
                var.key = variable.key
                var.is_secret = variable.is_secret
                var.encrypted_value = encrypted_value
                var.value = variable.value if not variable.is_secret else None

    async def delete_variable(self, environment_id: str, variable_id: str) -> None:
        if environment_id in self.variables:
            self.variables[environment_id] = [v for v in self.variables[environment_id] if str(v.id) != str(variable_id)]

    async def get_raw_variables(self, environment_id: str) -> List[OrmEnvironmentVariable]:
        return self.variables.get(environment_id, [])
        
    async def bind_pipeline(self, pipeline_id: str, environment_id: str) -> None:
        if pipeline_id not in self.bindings:
            self.bindings[pipeline_id] = set()
        self.bindings[pipeline_id].add(environment_id)
        
    async def unbind_pipeline(self, pipeline_id: str, environment_id: str) -> None:
        if pipeline_id in self.bindings and environment_id in self.bindings[pipeline_id]:
            self.bindings[pipeline_id].remove(environment_id)

    async def get_bound_environments(self, pipeline_id: str) -> List[Environment]:
        if pipeline_id not in self.bindings:
            return []
        return [self.environments[eid] for eid in self.bindings[pipeline_id] if eid in self.environments]
