from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from flowcore_shared.schemas.environment import Environment, EnvironmentVariable
from flowcore_server.db.environment_models import EnvironmentVariable as OrmEnvironmentVariable

class AbstractEnvironmentRepository(ABC):
    @abstractmethod
    async def create(self, environment: Environment) -> Environment:
        pass

    @abstractmethod
    async def get(self, environment_id: str) -> Optional[Environment]:
        pass

    @abstractmethod
    async def update(self, environment: Environment) -> Environment:
        pass

    @abstractmethod
    async def delete(self, environment_id: str) -> None:
        pass

    @abstractmethod
    async def list_by_workspace(self, workspace_id: str) -> List[Environment]:
        pass

    @abstractmethod
    async def add_variable(self, environment_id: str, variable: EnvironmentVariable, encrypted_value: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def update_variable(self, environment_id: str, variable: EnvironmentVariable, encrypted_value: Optional[str] = None) -> None:
        pass

    @abstractmethod
    async def delete_variable(self, environment_id: str, variable_id: str) -> None:
        pass

    @abstractmethod
    async def get_raw_variables(self, environment_id: str) -> List[OrmEnvironmentVariable]:
        """Returns the raw ORM variables (including encrypted_value) so the service can decrypt them."""
        pass
        
    @abstractmethod
    async def bind_pipeline(self, pipeline_id: str, environment_id: str) -> None:
        pass
        
    @abstractmethod
    async def unbind_pipeline(self, pipeline_id: str, environment_id: str) -> None:
        pass

    @abstractmethod
    async def get_bound_environments(self, pipeline_id: str) -> List[Environment]:
        pass
