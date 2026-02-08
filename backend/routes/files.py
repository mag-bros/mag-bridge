import logging
from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import shutil

from backend.config import SDF_DIR

files_router = APIRouter(prefix="/files", tags=["files"])
logger = logging.getLogger("uvicorn.access")

class FilePathRequest(BaseModel):
    path: str

@files_router.post("/upload")
async def upload_file(data: FilePathRequest):
    src = Path(data.path)

    if not src.exists():
        logger.info(f"Upload attempt: file does not exist: {src}")
        return {"error": "File does not exist"}

    dest = SDF_DIR / src.name

    shutil.copy2(src, dest)

    logger.info(f"SDF copied: {src} -> {dest}")

    return {
        "filename": src.name,
    }
