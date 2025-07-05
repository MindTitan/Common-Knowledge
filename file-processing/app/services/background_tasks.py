from app.core.database import SessionLocal
from app.services import upload_service


def upload_task(task_id: str) -> None:
    db = SessionLocal()
    try:
        upload_service.process_task(db, task_id)
    finally:
        db.close()
