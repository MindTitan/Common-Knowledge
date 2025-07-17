from abc import ABC, abstractmethod
from datetime import datetime


class BlobStorageException(Exception):
    pass


class BlobStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, source_file_path: str, destination_path: str) -> str:
        pass

    @abstractmethod
    def generate_download_url(self, blob_path: str) -> tuple[str, datetime]:
        pass

    @abstractmethod
    def file_exists(self, blob_path: str) -> bool:
        pass


def get_blob_storage_provider(provider_name: str) -> BlobStorageProvider:
    if provider_name == "s3":
        from app.services.s3_provider import s3_provider
        return s3_provider
    else:
        raise BlobStorageException(f"Invalid provider name: {provider_name}")


storage_provider = get_blob_storage_provider('s3')