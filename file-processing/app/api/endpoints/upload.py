from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.schemas import FileUploadRequest, FileUploadResponse, UploadTaskStatusResponse
from app.services.upload_service import create_task, get_task
from app.services.background_tasks import upload_task

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
def upload_file(
    request: FileUploadRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
) -> FileUploadResponse:
    task_id = create_task(db, request.source_file_path)
    background_tasks.add_task(upload_task, task_id)
    return FileUploadResponse(task_id=task_id) 


@router.get("/upload/{task_id}", response_model=UploadTaskStatusResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db_session)
) -> UploadTaskStatusResponse:
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 