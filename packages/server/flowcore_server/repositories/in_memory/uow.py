from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.repositories.in_memory.pipeline import InMemoryPipelineRepository
from flowcore_server.repositories.in_memory.execution import InMemoryExecutionRepository
from flowcore_server.repositories.in_memory.schedule import InMemoryScheduleRepository
from flowcore_server.repositories.in_memory.lineage import InMemoryLineageRepository
from flowcore_server.repositories.in_memory.environment import InMemoryEnvironmentRepository
from flowcore_server.repositories.in_memory.auth import (
    InMemoryUserRepository,
    InMemoryOrganizationRepository,
    InMemoryWorkspaceRepository,
    InMemoryRoleRepository,
    InMemoryWorkspaceMemberRepository
)

class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        # We instantiate them once so state persists across UoW contexts
        # For now, folders can be None in tests if they don't test folders
        self._pipelines = InMemoryPipelineRepository()
        self._folders = None
        self._executions = InMemoryExecutionRepository()
        self._schedules = InMemoryScheduleRepository()
        self._lineage = InMemoryLineageRepository()
        self._environments = InMemoryEnvironmentRepository()
        self._users = InMemoryUserRepository()
        self._organizations = InMemoryOrganizationRepository()
        self._workspaces = InMemoryWorkspaceRepository()
        self._roles = InMemoryRoleRepository()
        self._workspace_members = InMemoryWorkspaceMemberRepository()
        self.committed = False
        
    async def __aenter__(self) -> "InMemoryUnitOfWork":
        self.committed = False
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.committed = False

    @property
    def pipelines(self):
        return self._pipelines

    @property
    def folders(self):
        return self._folders
        
    @property
    def executions(self):
        return self._executions

    @property
    def schedules(self):
        return self._schedules

    @property
    def lineage(self):
        return self._lineage

    @property
    def environments(self):
        return self._environments

    @property
    def users(self):
        return self._users

    @property
    def organizations(self):
        return self._organizations

    @property
    def workspaces(self):
        return self._workspaces

    @property
    def roles(self):
        return self._roles

    @property
    def workspace_members(self):
        return self._workspace_members

    @property
    def api_keys(self):
        return None
        
    @property
    def audit_logs(self):
        return None
