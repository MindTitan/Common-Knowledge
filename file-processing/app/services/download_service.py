from app.schemas import DownloadFileResponse
from app.services.blob_storage import get_blob_storage_provider, BlobStorageException


def generate_download_url(blob_storage_path: str) -> DownloadFileResponse:
    """Generate a presigned download URL for a file in blob storage."""
    try:
        blob_storage = get_blob_storage_provider('s3')
        download_url, expires_at = blob_storage.generate_download_url(
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