from sqlalchemy.ext.asyncio import AsyncSession
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.repositories.postgres.pipeline import PostgresPipelineRepository
from flowcore_server.repositories.postgres.folder import PostgresFolderRepository
from flowcore_server.repositories.postgres.execution import PostgresExecutionRepository
from flowcore_server.repositories.postgres.schedule import PostgresScheduleRepository
from flowcore_server.repositories.postgres.environment import AsyncSqlAlchemyEnvironmentRepository as PostgresEnvironmentRepository
from flowcore_server.repositories.postgres.lineage import AsyncSqlAlchemyLineageRepository
from flowcore_server.repositories.postgres.auth import (
    AsyncSqlAlchemyUserRepository,
    AsyncSqlAlchemyOrganizationRepository,
    AsyncSqlAlchemyWorkspaceRepository,
    AsyncSqlAlchemyRoleRepository,
    AsyncSqlAlchemyWorkspaceMemberRepository
)
from flowcore_server.config.database import AsyncSessionLocal

class AsyncSqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        
    async def __aenter__(self) -> "AsyncSqlAlchemyUnitOfWork":
        self.session: AsyncSession = self.session_factory()
        self._pipelines = PostgresPipelineRepository(self.session)
        self._folders = PostgresFolderRepository(self.session)
        self._executions = PostgresExecutionRepository(self.session)
        self._schedules = PostgresScheduleRepository(self.session)
        self._environments = PostgresEnvironmentRepository(self.session)
        self._lineage = AsyncSqlAlchemyLineageRepository(self.session)
        self._users = AsyncSqlAlchemyUserRepository(self.session)
        self._organizations = AsyncSqlAlchemyOrganizationRepository(self.session)
        self._workspaces = AsyncSqlAlchemyWorkspaceRepository(self.session)
        self._roles = AsyncSqlAlchemyRoleRepository(self.session)
        self._workspace_members = AsyncSqlAlchemyWorkspaceMemberRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

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
    def environments(self):
        return self._environments

    @property
    def lineage(self):
        return self._lineage
