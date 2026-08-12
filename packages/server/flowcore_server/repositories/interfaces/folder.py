import abc
from typing import List, Optional
from flowcore.models.workspace import Folder

class AbstractFolderRepository(abc.ABC):
    @abc.abstractmethod
    async def create_folder(self, folder: Folder) -> Folder:
        pass

    @abc.abstractmethod
    async def get_folder(self, folder_id: str) -> Optional[Folder]:
        pass

    @abc.abstractmethod
    async def update_folder(self, folder_id: str, updates: dict) -> Optional[Folder]:
        pass

    @abc.abstractmethod
    async def delete_folder(self, folder_id: str) -> bool:
        pass

    @abc.abstractmethod
    async def list_folders(self) -> List[Folder]:
        pass
