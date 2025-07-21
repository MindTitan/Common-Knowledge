from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional


class BlobStorageException(Exception):
    pass


class BlobStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, source_file_path: str, destination_path: str) -> str:
        pass

    @abstractmethod
    def download_file(self, blob_path: str, local_file_path: str) -> bool:
        """Download a file from blob storage to local filesystem.
        
        Args:
            blob_path: Path of the file in blob storage
            local_file_path: Local path where the file should be saved
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        pass

    @abstractmethod
    def generate_download_url(self, path: str) -> tuple[str, datetime]:
        pass

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def generate_upload_urls(self, paths: List[str], content_type: Optional[str] = None, expires_in: Optional[int] = None) -> List[tuple[str, str, datetime]]:
        """Generate presigned upload URLs for multiple blob paths.
        
        Args:
            paths: List of blob paths to generate upload URLs for
            content_type: Optional content type for the upload
            expires_in: Optional expiration time in seconds
            
        Returns:
            List of tuples containing (path, upload_url, expires_at)
        """
        pass


def get_blob_storage_provider(provider_name: str) -> BlobStorageProvider:
    if provider_name == "s3":
        from app.services.s3_provider import s3_provider
        return s3_provider
    else:
        raise BlobStorageException(f"Invalid provider name: {provider_name}")


storage_provider = get_blob_storage_provider('s3')