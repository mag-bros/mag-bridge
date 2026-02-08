import logging
from fastapi import APIRouter
from pydantic import BaseModel
import os

files_router = APIRouter(prefix="/files", tags=["files"])
logger = logging.getLogger("uvicorn.access")

class FilePathRequest(BaseModel):
    path: str

@files_router.post("/upload")
async def upload_file(data: FilePathRequest):
    if not os.path.exists(data.path):
        logger.info(f"Upload attempt: file does not exist: {data.path}")
        return {"error": "File does not exist"}

    logger.info(f"File uploaded: {data.path}")
    return {
        "path": data.path,
        "filename": os.path.basename(data.path),
    }
