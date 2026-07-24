import uuid
from datetime import datetime
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_shared.schemas.auth import (
    UserInDB, Organization, Workspace, Role, Permission, WorkspaceMember
)
from flowcore_server.services.auth import AuthService

DEFAULT_ORG_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000002"
ADMIN_ROLE_ID = "00000000-0000-0000-0000-000000000003"
DEV_ROLE_ID = "00000000-0000-0000-0000-000000000004"
VIEWER_ROLE_ID = "00000000-0000-0000-0000-000000000005"

PERMISSIONS = [
    Permission(id="pipeline:create", name="Pipeline Create", description="Create pipelines"),
    Permission(id="pipeline:update", name="Pipeline Update", description="Update pipelines"),
    Permission(id="pipeline:delete", name="Pipeline Delete", description="Delete pipelines"),
    Permission(id="pipeline:execute", name="Pipeline Execute", description="Execute pipelines"),
    Permission(id="schedule:create", name="Schedule Create", description="Create schedules"),
    Permission(id="schedule:update", name="Schedule Update", description="Update schedules"),
    Permission(id="plugin:install", name="Plugin Install", description="Install plugins"),
    Permission(id="plugin:view", name="Plugin View", description="View plugins"),
    Permission(id="secret:view", name="Secret View", description="View secrets"),
    Permission(id="secret:update", name="Secret Update", description="Update secrets"),
    Permission(id="workspace:manage", name="Workspace Manage", description="Manage workspace settings"),
    Permission(id="environment:view", name="Environment View", description="View environments"),
    Permission(id="environment:edit", name="Environment Edit", description="Create and edit environments"),
    Permission(id="secret:manage", name="Secret Manage", description="Manage environment secrets"),
    Permission(id="audit:view", name="Audit View", description="View audit logs"),
    Permission(id="admin:*", name="Admin All", description="Full administrative access")
]

async def seed_default_data(uow: AbstractUnitOfWork):
    async with uow:
        # Check if admin user exists to avoid re-seeding everything
        if await uow.users.get_by_email("admin@flowcore.io"):
            return

        now = datetime.utcnow()

        # Create Default Organization if missing
        if not await uow.organizations.get(DEFAULT_ORG_ID):
            default_org = Organization(
                id=DEFAULT_ORG_ID,
                name="Default Organization",
                description="The primary organization for this instance.",
                created_at=now,
                updated_at=now
            )
            await uow.organizations.create(default_org)

        # Create Default Workspace if missing
        if not await uow.workspaces.get(DEFAULT_WORKSPACE_ID):
            default_ws = Workspace(
                id=DEFAULT_WORKSPACE_ID,
                name="Default Workspace",
                description="The default workspace.",
                organization_id=DEFAULT_ORG_ID,
                created_at=now,
                updated_at=now
            )
            await uow.workspaces.create(default_ws)

        # Create Roles if missing
        if not await uow.roles.get(ADMIN_ROLE_ID):
            admin_role = Role(
                id=ADMIN_ROLE_ID,
                name="Workspace Admin",
                organization_id=DEFAULT_ORG_ID,
                permissions=PERMISSIONS,
                created_at=now,
                updated_at=now
            )
            await uow.roles.create(admin_role)
            
        if not await uow.roles.get(DEV_ROLE_ID):
            dev_permissions = [p for p in PERMISSIONS if not p.id.startswith("admin:") and not p.id.startswith("workspace:")]
            dev_role = Role(
                id=DEV_ROLE_ID,
                name="Developer",
                organization_id=DEFAULT_ORG_ID,
                permissions=dev_permissions,
                created_at=now,
                updated_at=now
            )
            await uow.roles.create(dev_role)
            
        if not await uow.roles.get(VIEWER_ROLE_ID):
            viewer_permissions = [p for p in PERMISSIONS if p.id.endswith(":view")]
            viewer_role = Role(
                id=VIEWER_ROLE_ID,
                name="Viewer",
                organization_id=DEFAULT_ORG_ID,
                permissions=viewer_permissions,
                created_at=now,
                updated_at=now
            )
            await uow.roles.create(viewer_role)

        # Create Default Admin User
        admin_user_id = str(uuid.uuid4())
        hashed_password = AuthService.get_password_hash("admin")
        admin_user = UserInDB(
            id=admin_user_id,
            email="admin@flowcore.io",
            username="admin",
            full_name="FlowCore Admin",
            password_hash=hashed_password,
            created_at=now,
            updated_at=now
        )
        await uow.users.create(admin_user)

        # Assign Admin to Default Workspace
        admin_member = WorkspaceMember(
            user_id=admin_user_id,
            workspace_id=DEFAULT_WORKSPACE_ID,
            role_id=ADMIN_ROLE_ID,
            created_at=now
        )
        await uow.workspace_members.add_member(admin_member)

        # Migrate existing pipelines/schedules/executions to Default Workspace
        # For an in-memory implementation, this might be tricky, but we can set the workspace_id 
        # on all existing items if any exist (though they shouldn't exist on first run)
        
        await uow.commit()
