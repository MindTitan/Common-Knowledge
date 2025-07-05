from fastapi import APIRouter
from app.api.endpoints import upload, tasks, download

api_router = APIRouter()

api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(tasks.router, tags=["tasks"])
api_router.include_router(download.router, tags=["download"]) 