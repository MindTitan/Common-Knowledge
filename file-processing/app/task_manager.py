import uuid
from datetime import datetime
from typing import Optional
from app.models import TaskStatus, TaskStatusResponse
from app.blob_storage import get_blob_storage_provider, BlobStorageException
from app.config import settings
from app.db import get_db_cursor
import os


class TaskManager:
    def create_task(self, source_file_path: str) -> str:
        task_id = str(uuid.uuid4())
        now = datetime.now(datetime.UTC)
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO upload_tasks 
                (task_id, status, source_file_path, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (task_id, TaskStatus.PENDING, source_file_path, now, now))
        
        return task_id

    def get_task(self, task_id: str) -> Optional[TaskStatusResponse]:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT task_id, status, source_file_path, blob_storage_path, 
                       error_message, created_at, updated_at
                FROM upload_tasks 
                WHERE task_id = %s
            """, (task_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            return TaskStatusResponse(
                task_id=result['task_id'],
                status=TaskStatus(result['status']),
                source_file_path=result['source_file_path'],
                blob_storage_path=result['blob_storage_path'],
                error_message=result['error_message'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )

    def update_task_status(self, task_id: str, status: TaskStatus, blob_storage_path: Optional[str] = None, error_message: Optional[str] = None) -> None:
        with get_db_cursor() as cursor:
            update_fields = ["status = %s", "updated_at = %s"]
            params = [status, datetime.now(datetime.UTC)]
            
            if blob_storage_path:
                update_fields.append("blob_storage_path = %s")
                params.append(blob_storage_path)
            
            if error_message:
                update_fields.append("error_message = %s")
                params.append(error_message)
            
            params.append(task_id)
            
            cursor.execute(f"""
                UPDATE upload_tasks 
                SET {', '.join(update_fields)}
                WHERE task_id = %s
            """, params)

    def process_upload_task(self, task_id: str) -> None:
        task = self.get_task(task_id)
        if not task:
            return

        try:
            self.update_task_status(task_id, TaskStatus.PROCESSING)
            
            full_source_path = os.path.join(settings.source_path, task.source_file_path)
            destination_path = f"uploads/{task_id}/{os.path.basename(task.source_file_path)}"
            
            blob_storage = get_blob_storage_provider()
            blob_storage_path = blob_storage.upload_file(full_source_path, destination_path)
            
            self.update_task_status(task_id, TaskStatus.COMPLETED, blob_storage_path=blob_storage_path)
            
        except BlobStorageException as e:
            self.update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED, error_message=f"Unexpected error: {str(e)}")


task_manager = TaskManager() 