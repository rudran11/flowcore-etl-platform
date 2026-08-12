import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from flowcore.models.workspace import Folder
from flowcore_server.db.models import Folder as OrmFolder
from flowcore_server.repositories.interfaces.folder import AbstractFolderRepository
from flowcore_server.dependencies.context import get_workspace_id

def map_orm_to_folder(orm_obj: OrmFolder) -> Folder:
    return Folder(
        id=str(orm_obj.id),
        workspace_id=str(orm_obj.workspace_id) if orm_obj.workspace_id else "",
        name=orm_obj.name,
        parent_id=str(orm_obj.parent_id) if orm_obj.parent_id else None,
        color=orm_obj.color,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at
    )

def map_folder_to_orm(domain_obj: Folder) -> OrmFolder:
    return OrmFolder(
        id=uuid.UUID(domain_obj.id),
        workspace_id=uuid.UUID(domain_obj.workspace_id) if domain_obj.workspace_id else None,
        name=domain_obj.name,
        parent_id=uuid.UUID(domain_obj.parent_id) if domain_obj.parent_id else None,
        color=domain_obj.color,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at
    )

class PostgresFolderRepository(AbstractFolderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_folder(self, folder: Folder) -> Folder:
        orm_obj = map_folder_to_orm(folder)
        orm_obj.workspace_id = uuid.UUID(get_workspace_id())
        self.session.add(orm_obj)
        await self.session.flush()
        return map_orm_to_folder(orm_obj)

    async def get_folder(self, folder_id: str) -> Optional[Folder]:
        stmt = select(OrmFolder).where(OrmFolder.id == uuid.UUID(folder_id)).where(OrmFolder.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_folder(orm_obj)
        return None

    async def update_folder(self, folder_id: str, updates: dict) -> Optional[Folder]:
        stmt = select(OrmFolder).where(OrmFolder.id == uuid.UUID(folder_id)).where(OrmFolder.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        
        if not orm_obj:
            return None
            
        for key, value in updates.items():
            if hasattr(orm_obj, key):
                if key == 'parent_id' and value is not None:
                    setattr(orm_obj, key, uuid.UUID(value))
                elif key == 'parent_id' and value is None:
                    setattr(orm_obj, key, None)
                else:
                    setattr(orm_obj, key, value)
                
        await self.session.flush()
        return map_orm_to_folder(orm_obj)

    async def delete_folder(self, folder_id: str) -> bool:
        stmt = delete(OrmFolder).where(OrmFolder.id == uuid.UUID(folder_id)).where(OrmFolder.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def list_folders(self) -> List[Folder]:
        stmt = select(OrmFolder).where(OrmFolder.workspace_id == uuid.UUID(get_workspace_id())).order_by(OrmFolder.name.asc())
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        return [map_orm_to_folder(obj) for obj in orm_objs]
