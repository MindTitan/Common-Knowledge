from pydantic import BaseModel
from typing import Optional, List
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
    path: str

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

class FileUploadInfo(BaseModel):
    path: str
    content_type: str = "application/octet-stream"

class UploadUrlRequest(BaseModel):
    files: List[FileUploadInfo]
    expires_in: Optional[int] = None

class UploadUrlItem(BaseModel):
    path: str
    upload_url: str
    expires_at: datetime

class UploadUrlResponse(BaseModel):
    upload_urls: List[UploadUrlItem]

class FileDownloadItem(BaseModel):
    s3_path: str
    local_path: str

class DownloadToVolumeRequest(BaseModel):
    files: List[FileDownloadItem]

class FileDownloadResult(BaseModel):
    s3_path: str
    local_path: str
    status: str  # "success" or "failed"
    file_size: Optional[int] = None
    error_message: Optional[str] = None

class DownloadToVolumeResponse(BaseModel):
    total_files: int
    successful_downloads: int
    failed_downloads: int
    results: List[FileDownloadResult]

class DownloadTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    total_files: int
    successful_downloads: int = 0
    failed_downloads: int = 0
    results: List[FileDownloadResult] = []

class DownloadTaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    total_files: int
    completed_files: int
    failed_files: int
    results: List[FileDownloadResult]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# New schemas for delete functionality
class FileDeleteItem(BaseModel):
    local_path: str

class DeleteFromVolumeRequest(BaseModel):
    files: List[FileDeleteItem]

class FileDeleteResult(BaseModel):
    local_path: str
    status: str  # "success" or "failed"
    error_message: Optional[str] = None

class DeleteFromVolumeResponse(BaseModel):
    total_files: int
    successful_deletions: int
    failed_deletions: int
    results: List[FileDeleteResult]