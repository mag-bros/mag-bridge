import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil

from backend.config import SDF_DIR, translate_path, IS_DEV_MODE

files_router = APIRouter(prefix="/files", tags=["files"])
logger = logging.getLogger("uvicorn.access")

class FilePathRequest(BaseModel):
    path: str

@files_router.post("/upload")
async def upload_file(data: FilePathRequest):
    # Translate path (dev mode: macOS → container, prod mode: direct)
    try:
        src = translate_path(data.path)
        logger.info(f"Upload request: {data.path} → {src} (dev_mode={IS_DEV_MODE})")
    except HTTPException:
        # Re-raise HTTPException from translator
        raise
    except Exception as e:
        logger.error(f"Path translation error: {e}")
        raise HTTPException(status_code=500, detail="Internal path translation error")

    # Check if file exists (already checked in translate_path for dev mode)
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
