from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
from app.schemas import TaskStatus


class UploadTaskModel(Base):
    __tablename__ = "upload_tasks"

    task_id = Column(String(36), primary_key=True, index=True)
    status = Column(SQLEnum(TaskStatus), nullable=False)
    source_file_path = Column(Text, nullable=False)
    blob_storage_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
