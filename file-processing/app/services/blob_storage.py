from abc import ABC, abstractmethod
from typing import Optional


class BlobStorageException(Exception):
    pass


class BlobStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, source_file_path: str, destination_path: str) -> str:
        pass

    @abstractmethod
    def generate_download_url(self, blob_path: str, expiration_seconds: int = 3600) -> str:
        pass

    @abstractmethod
    def file_exists(self, blob_path: str) -> bool:
        pass


def get_blob_storage_provider() -> BlobStorageProvider:
    from app.services.s3 import get_s3_blob_storage_provider
    return get_s3_blob_storage_provider() 