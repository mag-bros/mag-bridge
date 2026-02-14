import logging
from fastapi import APIRouter, HTTPException
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

    # Check if file exists
    if not src.exists():
        logger.info(f"Upload attempt: file does not exist: {src}")
        raise HTTPException(status_code=400, detail="File does not exist")

    # Check file extension
    if src.suffix.lower() != ".sdf":
        logger.info(f"Upload attempt: invalid file type: {src}")
        raise HTTPException(status_code=400, detail="Only SDF files are allowed")

    # Optionally: check file is not empty
    if src.stat().st_size == 0:
        logger.info(f"Upload attempt: empty file: {src}")
        raise HTTPException(status_code=400, detail="File is empty")

    dest = SDF_DIR/src.name

    try:
        shutil.copy2(src, dest)
        logger.info(f"SDF copied: {src} -> {dest}")
    except Exception as e:
        logger.error(f"Failed to copy file {src} -> {dest}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    return {"filename": src.name}
