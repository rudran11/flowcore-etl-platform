import abc
from typing import Any
from flowcore_server.repositories.interfaces.pipeline import AbstractPipelineRepository
from flowcore_server.repositories.interfaces.execution import AbstractExecutionRepository
from flowcore_server.repositories.interfaces.schedule import AbstractScheduleRepository
from flowcore_server.repositories.interfaces.environment import AbstractEnvironmentRepository
from flowcore_server.repositories.interfaces.auth import (
    UserRepository,
    OrganizationRepository,
    WorkspaceRepository,
    RoleRepository,
    WorkspaceMemberRepository
)

class AbstractUnitOfWork(abc.ABC):
    """
    Abstract Unit of Work ensuring that multiple repository operations 
    can be coordinated in a single transactional boundary.
    """
    
    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pipelines(self) -> 'AbstractPipelineRepository':
        """Access the Pipeline Repository."""
        raise NotImplementedError
        
    @property
    @abc.abstractmethod
    def executions(self) -> 'AbstractExecutionRepository':
        """Access the Execution Repository."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def schedules(self) -> 'AbstractScheduleRepository':
        """Access the Schedule Repository."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def users(self) -> 'UserRepository':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def organizations(self) -> 'OrganizationRepository':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def workspaces(self) -> 'WorkspaceRepository':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def roles(self) -> 'RoleRepository':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def workspace_members(self) -> 'WorkspaceMemberRepository':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def environments(self) -> 'AbstractEnvironmentRepository':
        raise NotImplementedError
