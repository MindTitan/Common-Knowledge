from fastapi import FastAPI
from app.api import api_router
from app.core.database import engine
from app.models import UploadTask

app = FastAPI(title="File Processing API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    UploadTask.metadata.create_all(bind=engine)


app.include_router(api_router, prefix="/api/v1")
