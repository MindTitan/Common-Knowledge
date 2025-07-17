from app.schemas import DownloadFileResponse
from app.services.blob_storage import storage_provider, BlobStorageException


def generate_download_url(blob_storage_path: str) -> DownloadFileResponse:
    """Generate a presigned download URL for a file in blob storage."""
    try:
        download_url, expires_at = storage_provider.generate_download_url(
            blob_storage_path, 
        )
        return DownloadFileResponse(
            download_url=download_url,
            expires_at=expires_at
        )
    except BlobStorageException as e:
        raise ValueError(f"Blob storage error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to generate download URL: {str(e)}")