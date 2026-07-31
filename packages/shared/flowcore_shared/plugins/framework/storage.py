# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, BinaryIO, Optional, Tuple, List
from pydantic import BaseModel, Field

class StorageMetadata(BaseModel):
    name: str
    size_bytes: int
    content_type: Optional[str] = None
    last_modified: Optional[float] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

class StorageClient(ABC):
    """
    Base abstraction for Cloud & Storage connectors.
    Provides a uniform interface for Local, S3, GCS, Azure, etc.
    """
    
    @abstractmethod
    def list_files(self, prefix: str, recursive: bool = True) -> Iterator[StorageMetadata]:
        """List files in the storage system with the given prefix."""
        pass
        
    @abstractmethod
    def get_file_stream(self, path: str) -> BinaryIO:
        """Get a readable binary stream for the file."""
        pass
        
    @abstractmethod
    def upload_stream(self, path: str, stream: BinaryIO, metadata: Optional[StorageMetadata] = None) -> StorageMetadata:
        """Upload a binary stream to the path, optionally preserving metadata."""
        pass
        
    @abstractmethod
    def get_metadata(self, path: str) -> StorageMetadata:
        """Fetch metadata for a single file."""
        pass

# --- Architecture for Google Cloud Storage (GCS) ---
# To be implemented when `google-cloud-storage` dependency is introduced.
class GCSStorageClient(StorageClient):
    """
    Architecture stub for Google Cloud Storage.
    Would use `google.cloud.storage.Client` to interact with GCS buckets.
    """
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        self.bucket_name = bucket_name
        self.credentials_path = credentials_path
        # self.client = storage.Client.from_service_account_json(self.credentials_path)
        
    def list_files(self, prefix: str, recursive: bool = True) -> Iterator[StorageMetadata]:
        raise NotImplementedError("GCS implementation pending")
        
    def get_file_stream(self, path: str) -> BinaryIO:
        raise NotImplementedError("GCS implementation pending")
        
    def upload_stream(self, path: str, stream: BinaryIO, metadata: Optional[StorageMetadata] = None) -> StorageMetadata:
        raise NotImplementedError("GCS implementation pending")
        
    def get_metadata(self, path: str) -> StorageMetadata:
        raise NotImplementedError("GCS implementation pending")


# --- Architecture for Azure Blob Storage ---
# To be implemented when `azure-storage-blob` dependency is introduced.
class AzureBlobStorageClient(StorageClient):
    """
    Architecture stub for Azure Blob Storage.
    Would use `BlobServiceClient` from `azure.storage.blob`.
    """
    def __init__(self, connection_string: str, container_name: str):
        self.connection_string = connection_string
        self.container_name = container_name
        # self.client = BlobServiceClient.from_connection_string(self.connection_string)
        
    def list_files(self, prefix: str, recursive: bool = True) -> Iterator[StorageMetadata]:
        raise NotImplementedError("Azure Blob implementation pending")
        
    def get_file_stream(self, path: str) -> BinaryIO:
        raise NotImplementedError("Azure Blob implementation pending")
        
    def upload_stream(self, path: str, stream: BinaryIO, metadata: Optional[StorageMetadata] = None) -> StorageMetadata:
        raise NotImplementedError("Azure Blob implementation pending")
        
    def get_metadata(self, path: str) -> StorageMetadata:
        raise NotImplementedError("Azure Blob implementation pending")
