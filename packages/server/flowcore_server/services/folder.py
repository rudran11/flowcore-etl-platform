from typing import List, Optional
import uuid
from flowcore.models.workspace import Folder
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.schemas.workspace import FolderCreate, FolderUpdate, FolderResponse

from flowcore_server.dependencies.context import get_workspace_id

class FolderService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_folder(self, request: FolderCreate) -> Folder:
        async with self.uow as uow:
            folder = Folder(
                id=str(uuid.uuid4()),
                workspace_id=get_workspace_id(),
                name=request.name,
                parent_id=request.parent_id,
                color=request.color
            )
            created_folder = await uow.folders.create_folder(folder)
            await uow.commit()
            return created_folder

    async def get_folder(self, folder_id: str) -> FolderResponse:
        async with self.uow as uow:
            folder = await uow.folders.get_folder(folder_id)
            if not folder:
                raise ValueError(
                    'Not found',
                    detail=f"Folder {folder_id} not found"
                )
            
            # Get pipeline count
            pipelines = await uow.pipelines.list_pipelines(limit=1000, folder_id=folder_id)
            pipeline_count = len(pipelines)
            
            # Calculate last updated
            last_updated = None
            if pipelines:
                latest = max(pipelines, key=lambda p: p.updated_at if p.updated_at else p.created_at)
                last_updated = (latest.updated_at or latest.created_at).isoformat()

            return FolderResponse(
                folder=folder,
                pipeline_count=pipeline_count,
                last_updated=last_updated
            )

    async def update_folder(self, folder_id: str, request: FolderUpdate) -> Folder:
        updates = request.model_dump(exclude_unset=True)
        if not updates:
            async with self.uow as uow:
                folder = await uow.folders.get_folder(folder_id)
                if not folder:
                    raise ValueError('Not found')
                return folder

        async with self.uow as uow:
            updated_folder = await uow.folders.update_folder(folder_id, updates)
            if not updated_folder:
                raise ValueError(
                    'Not found',
                    detail=f"Folder {folder_id} not found"
                )
            await uow.commit()
            return updated_folder

    async def delete_folder(self, folder_id: str) -> None:
        async with self.uow as uow:
            # Check if there are pipelines inside
            pipelines = await uow.pipelines.list_pipelines(limit=1, folder_id=folder_id)
            if pipelines:
                raise ValueError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete folder containing pipelines"
                )

            success = await uow.folders.delete_folder(folder_id)
            if not success:
                raise ValueError(
                    'Not found',
                    detail=f"Folder {folder_id} not found"
                )
            await uow.commit()

    async def list_folders(self) -> List[FolderResponse]:
        async with self.uow as uow:
            folders = await uow.folders.list_folders()
            
            # Ideally this should be a single aggregative DB query, but for now we iterate.
            # In a real enterprise app, we'd add `get_folder_analytics` to the repo.
            responses = []
            for folder in folders:
                pipelines = await uow.pipelines.list_pipelines(limit=1000, folder_id=folder.id)
                pipeline_count = len(pipelines)
                last_updated = None
                if pipelines:
                    latest = max(pipelines, key=lambda p: p.updated_at if p.updated_at else p.created_at)
                    last_updated = (latest.updated_at or latest.created_at).isoformat()

                responses.append(FolderResponse(
                    folder=folder,
                    pipeline_count=pipeline_count,
                    last_updated=last_updated
                ))
            
            return responses
