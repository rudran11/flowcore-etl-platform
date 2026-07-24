from typing import List, Optional
from datetime import datetime
import uuid
from flowcore_shared.schemas.auth import UserInDB, Organization, Workspace, Role, WorkspaceMember
from flowcore_server.repositories.interfaces.auth import (
    UserRepository,
    OrganizationRepository,
    WorkspaceRepository,
    RoleRepository,
    WorkspaceMemberRepository
)

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users = {}

    async def create(self, user: UserInDB) -> UserInDB:
        self._users[user.id] = user
        return user

    async def get(self, user_id: str) -> Optional[UserInDB]:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        return next((u for u in self._users.values() if u.email == email), None)

    async def update(self, user_id: str, updates: dict) -> UserInDB:
        user = self._users.get(user_id)
        if not user:
            raise KeyError(f"User {user_id} not found")
        updated_data = user.model_dump()
        updated_data.update(updates)
        updated_data['updated_at'] = datetime.utcnow()
        new_user = UserInDB(**updated_data)
        self._users[user_id] = new_user
        return new_user

    async def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

class InMemoryOrganizationRepository(OrganizationRepository):
    def __init__(self):
        self._orgs = {}

    async def create(self, org: Organization) -> Organization:
        self._orgs[org.id] = org
        return org

    async def get(self, org_id: str) -> Optional[Organization]:
        return self._orgs.get(org_id)

    async def list_all(self) -> List[Organization]:
        return list(self._orgs.values())

class InMemoryWorkspaceRepository(WorkspaceRepository):
    def __init__(self):
        self._workspaces = {}

    async def create(self, workspace: Workspace) -> Workspace:
        self._workspaces[workspace.id] = workspace
        return workspace

    async def get(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

    async def get_by_organization(self, org_id: str) -> List[Workspace]:
        return [w for w in self._workspaces.values() if w.organization_id == org_id]

    async def list_all(self) -> List[Workspace]:
        return list(self._workspaces.values())

class InMemoryRoleRepository(RoleRepository):
    def __init__(self):
        self._roles = {}

    async def create(self, role: Role) -> Role:
        self._roles[role.id] = role
        return role

    async def get(self, role_id: str) -> Optional[Role]:
        return self._roles.get(role_id)

    async def get_by_name(self, name: str) -> Optional[Role]:
        return next((r for r in self._roles.values() if r.name == name), None)

    async def list_by_organization(self, org_id: Optional[str]) -> List[Role]:
        return [r for r in self._roles.values() if r.organization_id == org_id]

class InMemoryWorkspaceMemberRepository(WorkspaceMemberRepository):
    def __init__(self):
        self._members = []

    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        self._members.append(member)
        return member

    async def get_member(self, user_id: str, workspace_id: str) -> Optional[WorkspaceMember]:
        return next((m for m in self._members if m.user_id == user_id and m.workspace_id == workspace_id), None)

    async def list_by_workspace(self, workspace_id: str) -> List[WorkspaceMember]:
        return [m for m in self._members if m.workspace_id == workspace_id]

    async def list_by_user(self, user_id: str) -> List[WorkspaceMember]:
        return [m for m in self._members if m.user_id == user_id]
