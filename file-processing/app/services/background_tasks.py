from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.task_service import task_service


def process_upload_task_background(task_id: str) -> None:
    db = SessionLocal()
    try:
        task_service.process_upload_task(db, task_id)
    finally:
        db.close() 