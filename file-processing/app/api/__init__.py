from fastapi import APIRouter
from app.api.endpoints import upload, download, zip

api_router = APIRouter()

api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(download.router, tags=["download"])
api_router.include_router(zip.router, tags=["zip"])

__all__ = ["api_router"]
