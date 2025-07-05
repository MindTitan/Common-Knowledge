from fastapi import APIRouter, HTTPException
from app.schemas import DownloadFileRequest, DownloadFileResponse
from app.services import download_service

router = APIRouter()


@router.post("/download", response_model=DownloadFileResponse)
def generate_download_url(request: DownloadFileRequest) -> DownloadFileResponse:
    try:
        return download_service.generate_download_url(request.blob_storage_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}") 