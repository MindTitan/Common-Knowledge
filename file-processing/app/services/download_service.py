import os
import logging
import uuid
import requests
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta
from app.schemas import (
    DownloadFileResponse, 
    DownloadToVolumeRequest, 
    DownloadToVolumeResponse, 
    FileDownloadItem, 
    FileDownloadResult,
    DownloadTaskResponse,
    TaskStatus,
    DeleteFromVolumeRequest,
    DeleteFromVolumeResponse,
    FileDeleteItem,
    FileDeleteResult
)
from app.services.blob_storage import storage_provider, BlobStorageException

logger = logging.getLogger(__name__)

# Volume path configuration
VOLUME_PATH = '/app/data'

# In-memory task store for download tasks
_download_tasks: Dict[str, dict] = {}


def create_download_task(files: List[FileDownloadItem], callback: Optional = None) -> str:
    """Create a new download task in memory."""
    task_id = str(uuid.uuid4())
    
    _download_tasks[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "files": files,
        "callback": callback,
        "total_files": len(files),
        "completed_files": 0,
        "failed_files": 0,
        "results": [],
        "error_message": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    return task_id


def get_download_task(task_id: str) -> Optional[dict]:
    """Get download task status by task ID."""
    return _download_tasks.get(task_id)


def update_download_task(task_id: str, **updates) -> None:
    """Update download task status and related fields."""
    if task_id in _download_tasks:
        for key, value in updates.items():
            _download_tasks[task_id][key] = value
        _download_tasks[task_id]["updated_at"] = datetime.now()


def process_download_task(task_id: str) -> None:
    """Process a download task by downloading all files."""
    task_data = _download_tasks.get(task_id)
    if not task_data:
        logger.error(f"Download task {task_id} not found")
        return

    try:
        update_download_task(task_id, status=TaskStatus.PROCESSING)
        
        results: List[FileDownloadResult] = []
        successful_downloads = 0
        failed_downloads = 0
        
        for file_item in task_data["files"]:
            try:
                # Clean the s3_path - remove s3:// prefix if present
                clean_s3_path = file_item.s3_path
                if clean_s3_path.startswith('s3://'):
                    # Extract key from s3://bucket/key format
                    parts = clean_s3_path.replace('s3://', '').split('/', 1)
                    if len(parts) > 1:
                        clean_s3_path = parts[1]
                    else:
                        clean_s3_path = parts[0]
                
                # Use volume path configuration
                local_path_str = f"{VOLUME_PATH}/{file_item.local_path}"
                local_path = Path(local_path_str)
                
                # Ensure local directory exists
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file from blob storage to local path
                success = storage_provider.download_file(clean_s3_path, str(local_path))
                
                if success:
                    results.append(FileDownloadResult(
                        s3_path=file_item.s3_path,
                        local_path=str(local_path),
                        status="success",
                        file_size=local_path.stat().st_size if local_path.exists() else 0
                    ))
                    successful_downloads += 1
                    logger.info(f"Successfully downloaded {file_item.s3_path} to {local_path}")
                else:
                    results.append(FileDownloadResult(
                        s3_path=file_item.s3_path,
                        local_path=str(local_path),
                        status="failed",
                        error_message="Download failed - file may not exist"
                    ))
                    failed_downloads += 1
                    logger.error(f"Failed to download {file_item.s3_path}")
                    
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                results.append(FileDownloadResult(
                    s3_path=file_item.s3_path,
                    local_path=f"{VOLUME_PATH}/{file_item.local_path}",
                    status="failed",
                    error_message=error_msg
                ))
                failed_downloads += 1
                logger.error(f"Failed to download {file_item.s3_path}: {error_msg}")
        
        # Update task with final results
        update_download_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_files=successful_downloads,
            failed_files=failed_downloads,
            results=results
        )
        
        logger.info(f"Download task {task_id} completed: {successful_downloads} successful, {failed_downloads} failed")
        
        # Execute callback if provided
        callback = task_data.get("callback")
        if callback:
            execute_callback(task_id, callback, task_data)
        
    except Exception as e:
        error_msg = f"Download task failed: {str(e)}"
        update_download_task(
            task_id,
            status=TaskStatus.FAILED,
            error_message=error_msg
        )
        logger.error(f"Download task {task_id} failed: {error_msg}")
        
        # Execute callback even on failure if provided
        callback = task_data.get("callback")
        if callback:
            execute_callback(task_id, callback, task_data)


def execute_callback(task_id: str, callback, task_data: dict) -> None:
    """Execute the callback HTTP request exactly as configured."""
    try:
        # Prepare headers
        headers = callback.headers or {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        # Get method and body from the CallbackRequest object
        method = callback.method.upper()
        body_data = callback.body or {}
        
        # Make the callback request with only the configured data
        if method == "GET":
            response = requests.get(
                callback.url,
                headers=headers,
                params=body_data,
                timeout=30
            )
        else:  # POST, PUT, PATCH, etc.
            response = requests.request(
                method,
                callback.url,
                headers=headers,
                json=body_data,
                timeout=30
            )
        
        if response.status_code < 400:
            logger.info(f"Callback executed successfully for task {task_id}: {response.status_code}")
        else:
            logger.warning(f"Callback returned error status for task {task_id}: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to execute callback for task {task_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error executing callback for task {task_id}: {str(e)}")


def download_files_to_volume_async(request: DownloadToVolumeRequest) -> DownloadTaskResponse:
    """Start background download of multiple files from blob storage to local volume."""
    if not request.files:
        raise ValueError("No files specified for download")
    
    # Create download task with callback
    task_id = create_download_task(request.files, request.callback)
    
    return DownloadTaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        total_files=len(request.files),
        successful_downloads=0,
        failed_downloads=0,
        results=[]
    )


def delete_files_from_volume(request: DeleteFromVolumeRequest) -> DeleteFromVolumeResponse:
    """Delete multiple files from local volume."""
    if not request.files:
        raise ValueError("No files specified for deletion")
    
    results: List[FileDeleteResult] = []
    successful_deletions = 0
    failed_deletions = 0
    
    for file_item in request.files:
        try:
            # Use volume path configuration
            local_path_str = f"{VOLUME_PATH}/{file_item.local_path}"
            local_path = Path(local_path_str)
            
            if local_path.exists():
                if local_path.is_file():
                    local_path.unlink()  # Delete the file
                    results.append(FileDeleteResult(
                        local_path=str(local_path),
                        status="success"
                    ))
                    successful_deletions += 1
                    logger.info(f"Successfully deleted file {local_path}")
                elif local_path.is_dir():
                    import shutil
                    shutil.rmtree(local_path)  # Delete the folder and all contents
                    results.append(FileDeleteResult(
                        local_path=str(local_path),
                        status="success"
                    ))
                    successful_deletions += 1
                    logger.info(f"Successfully deleted folder {local_path}")
                else:
                    results.append(FileDeleteResult(
                        local_path=str(local_path),
                        status="failed",
                        error_message="Path exists but is neither a file nor a directory"
                    ))
                    failed_deletions += 1
                    logger.error(f"Failed to delete {local_path}: neither file nor directory")
            else:
                results.append(FileDeleteResult(
                    local_path=str(local_path),
                    status="failed",
                    error_message="File does not exist"
                ))
                failed_deletions += 1
                logger.warning(f"File does not exist: {local_path}")
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            results.append(FileDeleteResult(
                local_path=f"{VOLUME_PATH}/{file_item.local_path}",
                status="failed",
                error_message=error_msg
            ))
            failed_deletions += 1
            logger.error(f"Failed to delete {file_item.local_path}: {error_msg}")
    
    return DeleteFromVolumeResponse(
        total_files=len(request.files),
        successful_deletions=successful_deletions,
        failed_deletions=failed_deletions,
        results=results
    )


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


def download_files_to_volume(request: DownloadToVolumeRequest) -> DownloadToVolumeResponse:
    """Download multiple files from blob storage to local volume (synchronous - for backwards compatibility)."""
    if not request.files:
        raise ValueError("No files specified for download")
    
    results: List[FileDownloadResult] = []
    successful_downloads = 0
    failed_downloads = 0
    
    for file_item in request.files:
        try:
            # Clean the s3_path - remove s3:// prefix if present
            clean_s3_path = file_item.s3_path
            if clean_s3_path.startswith('s3://'):
                # Extract key from s3://bucket/key format
                parts = clean_s3_path.replace('s3://', '').split('/', 1)
                if len(parts) > 1:
                    clean_s3_path = parts[1]
                else:
                    clean_s3_path = parts[0]
            
            # Use volume path configuration
            local_path_str = f"{VOLUME_PATH}/{file_item.local_path}"
            local_path = Path(local_path_str)
            
            # Ensure local directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file from blob storage to local path
            success = storage_provider.download_file(clean_s3_path, str(local_path))
            
            if success:
                results.append(FileDownloadResult(
                    s3_path=file_item.s3_path,
                    local_path=str(local_path),
                    status="success",
                    file_size=local_path.stat().st_size if local_path.exists() else 0
                ))
                successful_downloads += 1
                logger.info(f"Successfully downloaded {file_item.s3_path} to {local_path}")
            else:
                results.append(FileDownloadResult(
                    s3_path=file_item.s3_path,
                    local_path=str(local_path),
                    status="failed",
                    error_message="Download failed - file may not exist"
                ))
                failed_downloads += 1
                logger.error(f"Failed to download {file_item.s3_path}")
                
        except BlobStorageException as e:
            error_msg = f"Blob storage error: {str(e)}"
            results.append(FileDownloadResult(
                s3_path=file_item.s3_path,
                local_path=f"{VOLUME_PATH}/{file_item.local_path}",
                status="failed",
                error_message=error_msg
            ))
            failed_downloads += 1
            logger.error(f"Failed to download {file_item.s3_path}: {error_msg}")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            results.append(FileDownloadResult(
                s3_path=file_item.s3_path,
                local_path=f"{VOLUME_PATH}/{file_item.local_path}",
                status="failed",
                error_message=error_msg
            ))
            failed_downloads += 1
            logger.error(f"Failed to download {file_item.s3_path}: {error_msg}")
    
    return DownloadToVolumeResponse(
        total_files=len(request.files),
        successful_downloads=successful_downloads,
        failed_downloads=failed_downloads,
        results=results
    )