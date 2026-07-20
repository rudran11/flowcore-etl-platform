from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from flowcore_shared.schemas.pipeline import Pipeline, PipelineVersion
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
        self.session.add(orm_obj)
        await self.session.flush()
        return map_orm_to_pipeline(orm_obj)

    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        stmt = select(OrmPipeline).where(OrmPipeline.id == pipeline_id).where(OrmPipeline.is_deleted == False)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline(orm_obj)
        return None

    async def get_pipeline_by_name(self, name: str) -> Optional[Pipeline]:
        stmt = select(OrmPipeline).where(OrmPipeline.name == name).where(OrmPipeline.is_deleted == False)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline(orm_obj)
        return None

    async def list_pipelines(self) -> List[Pipeline]:
        stmt = select(OrmPipeline).where(OrmPipeline.is_deleted == False)
        result = await self.session.execute(stmt)
        orm_objs = result.scalars().all()
        return [map_orm_to_pipeline(obj) for obj in orm_objs]

    async def delete_pipeline(self, pipeline_id: str) -> bool:
        stmt = select(OrmPipeline).where(OrmPipeline.id == pipeline_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            orm_obj.is_deleted = True
            await self.session.flush()
            return True
        return False

    async def create_pipeline_version(self, version: PipelineVersion) -> PipelineVersion:
        # Map version domain object to ORM
        # Assuming we just store the steps in dsl_definition for now as it wasn't strictly defined
        orm_obj = OrmPipelineVersion(
            id=version.id,
            pipeline_id=version.pipeline_id,
            version_tag=version.version,
            dsl_definition={"steps": [s.model_dump() for s in version.steps]},
            graph_definition={}
        )
        self.session.add(orm_obj)
        await self.session.flush()
        return version

    async def get_pipeline_version(self, pipeline_id: str, version_tag: str) -> Optional[PipelineVersion]:
        stmt = select(OrmPipelineVersion).where(
            OrmPipelineVersion.pipeline_id == pipeline_id,
            OrmPipelineVersion.version_tag == version_tag
        )
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline_version(orm_obj)
        return None

    async def get_pipeline_version_by_id(self, version_id: str) -> Optional[PipelineVersion]:
        stmt = select(OrmPipelineVersion).where(OrmPipelineVersion.id == version_id)
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return map_orm_to_pipeline_version(orm_obj)
        return None

    async def count_pipelines(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count(OrmPipeline.id)).where(OrmPipeline.is_deleted == False)
        result = await self.session.execute(stmt)
        return result.scalar_one()
