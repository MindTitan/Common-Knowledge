import uuid
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.models.upload_task import UploadTask
from app.schemas import TaskStatus, TaskStatusResponse
from app.services import get_blob_storage_provider, BlobStorageException
from app.core.config import settings


def create_upload_task(db: Session, source_file_path: str) -> str:
    """Create a new upload task in the database."""
    task_id = str(uuid.uuid4())
    
    db_task = UploadTask(
        task_id=task_id,
        status=TaskStatus.PENDING,
        source_file_path=source_file_path
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return task_id


def get_task(db: Session, task_id: str) -> Optional[TaskStatusResponse]:
    """Get task status by task ID."""
    db_task = db.query(UploadTask).filter(UploadTask.task_id == task_id).first()
    if not db_task:
        return None
    
    return TaskStatusResponse.model_validate(db_task)


def update_task_status(db: Session, task_id: str, status: TaskStatus, blob_storage_path: Optional[str] = None, error_message: Optional[str] = None) -> None:
    """Update task status and related fields."""
    db_task = db.query(UploadTask).filter(UploadTask.task_id == task_id).first()
    if db_task:
        db_task.status = status
        if blob_storage_path:
            db_task.blob_storage_path = blob_storage_path
        if error_message:
            db_task.error_message = error_message
        
        db.commit()


def process_upload_task(db: Session, task_id: str) -> None:
    """Process an upload task by uploading the file to blob storage."""
    task = get_task(db, task_id)
    if not task:
        return

    try:
        update_task_status(db, task_id, TaskStatus.PROCESSING)
        
        full_source_path = os.path.join(settings.source_path, task.source_file_path)
        destination_path = f"uploads/{task_id}/{os.path.basename(task.source_file_path)}"
        
        blob_storage = get_blob_storage_provider('s3')
        blob_storage_path = blob_storage.upload_file(full_source_path, destination_path)
        
        update_task_status(db, task_id, TaskStatus.COMPLETED, blob_storage_path=blob_storage_path)
        
    except BlobStorageException as e:
        update_task_status(db, task_id, TaskStatus.FAILED, error_message=str(e))
    except Exception as e:
        update_task_status(db, task_id, TaskStatus.FAILED, error_message=f"Unexpected error: {str(e)}")