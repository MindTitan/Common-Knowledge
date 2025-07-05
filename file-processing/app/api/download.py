from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.schemas.upload_task import DownloadFileRequest, DownloadFileResponse
from app.services import get_blob_storage_provider, BlobStorageException
from app.core.config import settings

router = APIRouter()


@router.post("/download", response_model=DownloadFileResponse)
def generate_download_url(request: DownloadFileRequest) -> DownloadFileResponse:
    try:
        blob_storage = get_blob_storage_provider()
        download_url = blob_storage.generate_download_url(
            request.blob_storage_path, 
            settings.s3_presigned_url_expiration
        )
        
        expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(seconds=settings.s3_presigned_url_expiration)
        
        return DownloadFileResponse(
            download_url=download_url,
            expires_at=expires_at
        )
    except BlobStorageException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}") 