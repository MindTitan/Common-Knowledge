from fastapi import FastAPI, BackgroundTasks, HTTPException

from app.models import (
    FileUploadRequest, FileUploadResponse, 
    TaskStatusResponse, DownloadFileRequest, DownloadFileResponse
)
from app.task_manager import task_manager
from app.blob_storage import get_blob_storage_provider, BlobStorageException
from app.db import init_database
from datetime import datetime, timedelta
from app.config import settings

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    init_database()


@app.post("/upload", response_model=FileUploadResponse)
def upload_file(request: FileUploadRequest, background_tasks: BackgroundTasks) -> FileUploadResponse:
    task_id = task_manager.create_task(request.source_file_path)
    background_tasks.add_task(task_manager.process_upload_task, task_id)
    return FileUploadResponse(task_id=task_id)


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str) -> TaskStatusResponse:
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/download", response_model=DownloadFileResponse)
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
