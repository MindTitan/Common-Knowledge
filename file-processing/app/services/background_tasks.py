from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services import upload_service


def process_upload_task_background(task_id: str) -> None:
    db = SessionLocal()
    try:
        upload_service.process_upload_task(db, task_id)
    finally:
        db.close() 