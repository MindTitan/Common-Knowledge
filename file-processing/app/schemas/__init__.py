from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadRequest(BaseModel):
    source_file_path: str


class FileUploadResponse(BaseModel):
    task_id: str
    status: str = "pending"


class DownloadFileRequest(BaseModel):
    blob_storage_path: str


class DownloadFileResponse(BaseModel):
    download_url: str
    expires_at: datetime

class UploadTaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    source_file_path: str
    blob_storage_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True