from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.schemas.upload_task import TaskStatusResponse
from app.services import task_service

router = APIRouter()


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db_session)
) -> TaskStatusResponse:
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 