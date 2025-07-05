from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.schemas.upload_task import FileUploadRequest, FileUploadResponse
from app.services import task_service, process_upload_task_background

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
def upload_file(
    request: FileUploadRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
) -> FileUploadResponse:
    task_id = task_service.create_task(db, request.source_file_path)
    background_tasks.add_task(process_upload_task_background, task_id)
    return FileUploadResponse(task_id=task_id) 