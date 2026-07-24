import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from flowcore_shared.schemas.auth import UserInDB, Organization, Workspace, Role, WorkspaceMember, Permission
from flowcore_server.db.auth_models import (
    User as UserModel,
    Organization as OrganizationModel,
    Workspace as WorkspaceModel,
    Role as RoleModel,
    Permission as PermissionModel,
    RolePermission as RolePermissionModel,
    WorkspaceMember as WorkspaceMemberModel
)
from flowcore_server.repositories.interfaces.auth import (
    UserRepository, OrganizationRepository, WorkspaceRepository, RoleRepository, WorkspaceMemberRepository
)

class AsyncSqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserInDB) -> UserInDB:
        db_user = UserModel(
            id=uuid.UUID(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            password_hash=user.password_hash,
            avatar=user.avatar,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        self.session.add(db_user)
        return user

    async def get(self, user_id: str) -> Optional[UserInDB]:
        stmt = select(UserModel).where(UserModel.id == uuid.UUID(user_id))
        result = await self.session.execute(stmt)
        db_user = result.scalars().first()
        if not db_user:
            return None
        return UserInDB(
            id=str(db_user.id),
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            password_hash=db_user.password_hash,
            avatar=db_user.avatar,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalars().first()
        if not db_user:
            return None
        return UserInDB(
            id=str(db_user.id),
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            password_hash=db_user.password_hash,
            avatar=db_user.avatar,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )

    async def update(self, user_id: str, updates: dict) -> UserInDB:
        stmt = select(UserModel).where(UserModel.id == uuid.UUID(user_id))
        result = await self.session.execute(stmt)
        db_user = result.scalars().first()
        if db_user:
            for k, v in updates.items():
                setattr(db_user, k, v)
            await self.session.flush()
            return UserInDB(
                id=str(db_user.id),
                email=db_user.email,
                username=db_user.username,
                full_name=db_user.full_name,
                password_hash=db_user.password_hash,
                avatar=db_user.avatar,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
                last_login=db_user.last_login
            )
        raise ValueError("User not found")

    async def delete(self, user_id: str) -> bool:
        stmt = select(UserModel).where(UserModel.id == uuid.UUID(user_id))
        result = await self.session.execute(stmt)
        db_user = result.scalars().first()
        if db_user:
            await self.session.delete(db_user)
            return True
        return False

class AsyncSqlAlchemyOrganizationRepository(OrganizationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, org: Organization) -> Organization:
        db_org = OrganizationModel(
            id=uuid.UUID(org.id),
            name=org.name,
            description=org.description,
            created_at=org.created_at,
            updated_at=org.updated_at
        )
        self.session.add(db_org)
        return org

    async def get(self, org_id: str) -> Optional[Organization]:
        stmt = select(OrganizationModel).where(OrganizationModel.id == uuid.UUID(org_id))
        result = await self.session.execute(stmt)
        db_org = result.scalars().first()
        if db_org:
            return Organization(
                id=str(db_org.id),
                name=db_org.name,
                description=db_org.description,
                created_at=db_org.created_at,
                updated_at=db_org.updated_at
            )
        return None

    async def list_all(self) -> List[Organization]:
        stmt = select(OrganizationModel)
        result = await self.session.execute(stmt)
        return [Organization(
            id=str(o.id),
            name=o.name,
            description=o.description,
            created_at=o.created_at,
            updated_at=o.updated_at
        ) for o in result.scalars().all()]

class AsyncSqlAlchemyWorkspaceRepository(WorkspaceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workspace: Workspace) -> Workspace:
        db_ws = WorkspaceModel(
            id=uuid.UUID(workspace.id),
            organization_id=uuid.UUID(workspace.organization_id),
            name=workspace.name,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at
        )
        self.session.add(db_ws)
        return workspace

    async def get(self, workspace_id: str) -> Optional[Workspace]:
        stmt = select(WorkspaceModel).where(WorkspaceModel.id == uuid.UUID(workspace_id))
        result = await self.session.execute(stmt)
        db_ws = result.scalars().first()
        if db_ws:
            return Workspace(
                id=str(db_ws.id),
                organization_id=str(db_ws.organization_id),
                name=db_ws.name,
                description=db_ws.description,
                created_at=db_ws.created_at,
                updated_at=db_ws.updated_at
            )
        return None

    async def get_by_organization(self, org_id: str) -> List[Workspace]:
        stmt = select(WorkspaceModel).where(WorkspaceModel.organization_id == uuid.UUID(org_id))
        result = await self.session.execute(stmt)
        return [Workspace(
            id=str(w.id),
            organization_id=str(w.organization_id),
            name=w.name,
            description=w.description,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in result.scalars().all()]

    async def list_all(self) -> List[Workspace]:
        stmt = select(WorkspaceModel)
        result = await self.session.execute(stmt)
        return [Workspace(
            id=str(w.id),
            organization_id=str(w.organization_id),
            name=w.name,
            description=w.description,
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in result.scalars().all()]

class AsyncSqlAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: Role) -> Role:
        stmt = select(RoleModel).where(RoleModel.id == uuid.UUID(role.id))
        res = await self.session.execute(stmt)
        if not res.scalars().first():
            db_role = RoleModel(
                id=uuid.UUID(role.id),
                name=role.name,
                description=role.description
            )
            self.session.add(db_role)
            
            for p in role.permissions:
                p_stmt = select(PermissionModel).where(PermissionModel.name == p.name)
                p_res = await self.session.execute(p_stmt)
                db_perm = p_res.scalars().first()
                if not db_perm:
                    # Usually permissions should be predefined, but if they don't exist we add them
                    # UUID for permission is a bit tricky, but p.id is fine
                    db_perm = PermissionModel(id=uuid.UUID(p.id) if '-' in p.id else uuid.uuid4(), name=p.name, description=p.description)
                    self.session.add(db_perm)
                    await self.session.flush()
                
                rp = RolePermissionModel(role_id=db_role.id, permission_id=db_perm.id)
                self.session.add(rp)

        return role

    async def get(self, role_id: str) -> Optional[Role]:
        stmt = select(RoleModel).options(selectinload(RoleModel.role_permissions).selectinload(RolePermissionModel.permission)).where(RoleModel.id == uuid.UUID(role_id))
        result = await self.session.execute(stmt)
        db_role = result.scalars().first()
        if db_role:
            perms = [Permission(id=str(rp.permission.id), name=rp.permission.name, description=rp.permission.description) for rp in db_role.role_permissions]
            return Role(
                id=str(db_role.id),
                name=db_role.name,
                description=db_role.description,
                permissions=perms,
                created_at=db_role.created_at,
                updated_at=db_role.updated_at
            )
        return None

    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = select(RoleModel).options(selectinload(RoleModel.role_permissions).selectinload(RolePermissionModel.permission)).where(RoleModel.name == name)
        result = await self.session.execute(stmt)
        db_role = result.scalars().first()
        if db_role:
            perms = [Permission(id=str(rp.permission.id), name=rp.permission.name, description=rp.permission.description) for rp in db_role.role_permissions]
            return Role(
                id=str(db_role.id),
                name=db_role.name,
                description=db_role.description,
                permissions=perms,
                created_at=db_role.created_at,
                updated_at=db_role.updated_at
            )
        return None

    async def list_by_organization(self, org_id: Optional[str]) -> List[Role]:
        stmt = select(RoleModel).options(selectinload(RoleModel.role_permissions).selectinload(RolePermissionModel.permission))
        result = await self.session.execute(stmt)
        roles = []
        for db_role in result.scalars().all():
            perms = [Permission(id=str(rp.permission.id), name=rp.permission.name, description=rp.permission.description) for rp in db_role.role_permissions]
            roles.append(Role(
                id=str(db_role.id),
                name=db_role.name,
                description=db_role.description,
                permissions=perms,
                created_at=db_role.created_at,
                updated_at=db_role.updated_at
            ))
        return roles

class AsyncSqlAlchemyWorkspaceMemberRepository(WorkspaceMemberRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        db_member = WorkspaceMemberModel(
            workspace_id=uuid.UUID(member.workspace_id),
            user_id=uuid.UUID(member.user_id),
            role_id=uuid.UUID(member.role_id),
            joined_at=member.created_at,
            created_at=member.created_at,
            updated_at=member.created_at
        )
        self.session.add(db_member)
        return member

    async def get_member(self, user_id: str, workspace_id: str) -> Optional[WorkspaceMember]:
        stmt = select(WorkspaceMemberModel).where(
            WorkspaceMemberModel.user_id == uuid.UUID(user_id),
            WorkspaceMemberModel.workspace_id == uuid.UUID(workspace_id)
        )
        result = await self.session.execute(stmt)
        db_member = result.scalars().first()
        if db_member:
            return WorkspaceMember(
                user_id=str(db_member.user_id),
                workspace_id=str(db_member.workspace_id),
                role_id=str(db_member.role_id),
                created_at=db_member.created_at
            )
        return None

    async def list_by_workspace(self, workspace_id: str) -> List[WorkspaceMember]:
        stmt = select(WorkspaceMemberModel).where(WorkspaceMemberModel.workspace_id == uuid.UUID(workspace_id))
        result = await self.session.execute(stmt)
        return [WorkspaceMember(
            user_id=str(m.user_id),
            workspace_id=str(m.workspace_id),
            role_id=str(m.role_id),
            created_at=m.created_at
        ) for m in result.scalars().all()]

    async def list_by_user(self, user_id: str) -> List[WorkspaceMember]:
        stmt = select(WorkspaceMemberModel).where(WorkspaceMemberModel.user_id == uuid.UUID(user_id))
        result = await self.session.execute(stmt)
        return [WorkspaceMember(
            user_id=str(m.user_id),
            workspace_id=str(m.workspace_id),
            role_id=str(m.role_id),
            created_at=m.created_at
        ) for m in result.scalars().all()]
