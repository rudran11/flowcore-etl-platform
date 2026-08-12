from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

import uuid
from flowcore.models.pipeline import Pipeline, PipelineVersion
from flowcore_server.dependencies.context import get_workspace_id
from flowcore_server.repositories.interfaces.pipeline import AbstractPipelineRepository
from flowcore_server.db.models import Pipeline as OrmPipeline
from flowcore_server.db.models import PipelineVersion as OrmPipelineVersion
from flowcore_server.repositories.mappers.pipeline import (
    map_orm_to_pipeline, map_pipeline_to_orm, map_orm_to_pipeline_version
)

class PostgresPipelineRepository(AbstractPipelineRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pipeline(self, pipeline: Pipeline) -> Pipeline:
        orm_obj = map_pipeline_to_orm(pipeline)
        orm_obj.workspace_id = uuid.UUID(get_workspace_id())
        self.session.add(orm_obj)
        await self.session.flush()
        return map_orm_to_pipeline(orm_obj)

    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        stmt = select(OrmPipeline).where(OrmPipeline.id == pipeline_id).where(OrmPipeline.is_deleted == False).where(OrmPipeline.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline(orm_obj)
        return None

    async def update_pipeline(self, pipeline_id: str, updates: dict) -> Optional[Pipeline]:
        stmt = select(OrmPipeline).where(OrmPipeline.id == pipeline_id).where(OrmPipeline.is_deleted == False).where(OrmPipeline.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        
        if not orm_obj:
            return None
            
        for key, value in updates.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)
                
        await self.session.flush()
        return map_orm_to_pipeline(orm_obj)

    async def get_pipeline_by_name(self, name: str) -> Optional[Pipeline]:
        stmt = select(OrmPipeline).where(OrmPipeline.name == name).where(OrmPipeline.is_deleted == False).where(OrmPipeline.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline(orm_obj)
        return None

    async def list_pipelines(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        user_id: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc"
    ) -> List[Pipeline]:
        from sqlalchemy import or_
        from flowcore_server.db.models import UserPipelineFavorite
        
        stmt = select(OrmPipeline).where(OrmPipeline.is_deleted == False).where(OrmPipeline.workspace_id == uuid.UUID(get_workspace_id()))
        
        if is_archived is not None:
            stmt = stmt.where(OrmPipeline.is_archived == is_archived)
            
        if folder_id is not None:
            if folder_id == "root":
                stmt = stmt.where(OrmPipeline.folder_id.is_(None))
            else:
                stmt = stmt.where(OrmPipeline.folder_id == uuid.UUID(folder_id))
                
        if is_favorite is not None and user_id is not None:
            if is_favorite:
                stmt = stmt.join(UserPipelineFavorite, OrmPipeline.id == UserPipelineFavorite.pipeline_id).where(UserPipelineFavorite.user_id == uuid.UUID(user_id))
            else:
                stmt = stmt.outerjoin(UserPipelineFavorite, (OrmPipeline.id == UserPipelineFavorite.pipeline_id) & (UserPipelineFavorite.user_id == uuid.UUID(user_id)))
                stmt = stmt.where(UserPipelineFavorite.pipeline_id.is_(None))
        
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    OrmPipeline.name.ilike(search_pattern),
                    OrmPipeline.description.ilike(search_pattern)
                )
            )
        
        if tags:
            # Assuming tags is a JSONB list of strings for now (will switch to Tag mapping if requested)
            stmt = stmt.where(OrmPipeline.tags.contains(tags))
            
        # Sorting
        order_col = OrmPipeline.created_at
        if sort_by == "name":
            order_col = OrmPipeline.name
        elif sort_by == "updated_at":
            order_col = OrmPipeline.updated_at
            
        if sort_order == "asc":
            stmt = stmt.offset(skip).limit(limit).order_by(order_col.asc())
        else:
            stmt = stmt.offset(skip).limit(limit).order_by(order_col.desc())
            
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        
        favorites_set = set()
        if user_id:
            fav_stmt = select(UserPipelineFavorite.pipeline_id).where(UserPipelineFavorite.user_id == uuid.UUID(user_id))
            fav_result = await self.session.execute(fav_stmt)
            favorites_set = {str(pid) for pid in fav_result.scalars().all()}
            
        pipelines = []
        for obj in orm_objs:
            p = map_orm_to_pipeline(obj)
            if user_id:
                p = p.model_copy(update={"is_favorite": str(p.id) in favorites_set})
            pipelines.append(p)
            
        return pipelines

    async def delete_pipeline(self, pipeline_id: str) -> bool:
        stmt = select(OrmPipeline).where(OrmPipeline.id == pipeline_id).where(OrmPipeline.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            orm_obj.is_deleted = True
            await self.session.flush()
            return True
        return False

    async def set_favorite(self, pipeline_id: str, user_id: str, is_favorite: bool) -> None:
        from flowcore_server.db.models import UserPipelineFavorite
        if is_favorite:
            stmt = select(UserPipelineFavorite).where(UserPipelineFavorite.pipeline_id == uuid.UUID(pipeline_id), UserPipelineFavorite.user_id == uuid.UUID(user_id))
            result = await self.session.execute(stmt)
            if not result.scalar_one_or_none():
                fav = UserPipelineFavorite(pipeline_id=uuid.UUID(pipeline_id), user_id=uuid.UUID(user_id))
                self.session.add(fav)
        else:
            stmt = delete(UserPipelineFavorite).where(UserPipelineFavorite.pipeline_id == uuid.UUID(pipeline_id), UserPipelineFavorite.user_id == uuid.UUID(user_id))
            await self.session.execute(stmt)
        await self.session.flush()

    async def create_pipeline_version(self, version: PipelineVersion) -> PipelineVersion:
        # Map version domain object to ORM
        orm_obj = OrmPipelineVersion(
            id=version.id,
            workspace_id=uuid.UUID(get_workspace_id()),
            pipeline_id=version.pipeline_id,
            version_tag=version.version,
            dsl_definition=version.dsl_definition or {"steps": [s.model_dump() for s in version.steps]},
            graph_definition=version.graph_definition or {}
        )
        self.session.add(orm_obj)
        await self.session.flush()
        return version

    async def get_pipeline_version(self, pipeline_id: str, version_tag: str) -> Optional[PipelineVersion]:
        stmt = select(OrmPipelineVersion).where(
            OrmPipelineVersion.pipeline_id == pipeline_id,
            OrmPipelineVersion.version_tag == version_tag,
            OrmPipelineVersion.workspace_id == uuid.UUID(get_workspace_id())
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline_version(orm_obj)
        return None

    async def get_pipeline_version_by_id(self, version_id: str) -> Optional[PipelineVersion]:
        stmt = select(OrmPipelineVersion).where(OrmPipelineVersion.id == version_id, OrmPipelineVersion.workspace_id == uuid.UUID(get_workspace_id()))
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline_version(orm_obj)
        return None

    async def list_pipeline_versions(self, pipeline_id: str) -> List[PipelineVersion]:
        stmt = select(OrmPipelineVersion).where(OrmPipelineVersion.pipeline_id == pipeline_id, OrmPipelineVersion.workspace_id == uuid.UUID(get_workspace_id())).order_by(OrmPipelineVersion.created_at.desc())
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        return [map_orm_to_pipeline_version(obj) for obj in orm_objs]

    async def count_pipelines(
        self,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        user_id: Optional[str] = None
    ) -> int:
        from sqlalchemy import or_, func
        from flowcore_server.db.models import UserPipelineFavorite
        
        stmt = select(func.count(OrmPipeline.id)).where(OrmPipeline.is_deleted == False).where(OrmPipeline.workspace_id == uuid.UUID(get_workspace_id()))
        
        if is_archived is not None:
            stmt = stmt.where(OrmPipeline.is_archived == is_archived)
            
        if folder_id is not None:
            if folder_id == "root":
                stmt = stmt.where(OrmPipeline.folder_id.is_(None))
            else:
                stmt = stmt.where(OrmPipeline.folder_id == uuid.UUID(folder_id))
                
        if is_favorite is not None and user_id is not None:
            if is_favorite:
                stmt = stmt.join(UserPipelineFavorite, OrmPipeline.id == UserPipelineFavorite.pipeline_id).where(UserPipelineFavorite.user_id == uuid.UUID(user_id))
            else:
                stmt = stmt.outerjoin(UserPipelineFavorite, (OrmPipeline.id == UserPipelineFavorite.pipeline_id) & (UserPipelineFavorite.user_id == uuid.UUID(user_id)))
                stmt = stmt.where(UserPipelineFavorite.pipeline_id.is_(None))
        
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    OrmPipeline.name.ilike(search_pattern),
                    OrmPipeline.description.ilike(search_pattern)
                )
            )
        
        if tags:
            stmt = stmt.where(OrmPipeline.tags.contains(tags))
            
        result = await self.session.execute(stmt)
        return result.scalar_one()
