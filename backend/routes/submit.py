import logging
from pathlib import Path
import shutil

from fastapi import APIRouter, HTTPException
from backend.config import SDF_DIR
from backend.schemas.calculations import CalculationRequest, InputType

router = APIRouter(prefix="/calculations", tags=["calculations"])
logger = logging.getLogger("uvicorn.access")

@router.post("/submit")
async def submit_calculation(data: CalculationRequest):
    if data.input_type == InputType.SDF:
        if not data.path:
            raise HTTPException(status_code=400, detail="Path is required for SDF input")
        
        src = Path(data.path)

        # Check if file exists
        if not src.exists():
            logger.info(f"Calculation attempt: file does not exist: {src}")
            raise HTTPException(status_code=400, detail="File does not exist")

        # Check file extension
        if src.suffix.lower() != ".sdf":
            logger.info(f"Calculation attempt: invalid file type: {src}")
            raise HTTPException(status_code=400, detail="Only SDF files are allowed")

        # Optionally: check file is not empty
        if src.stat().st_size == 0:
            logger.info(f"Calculation attempt: empty file: {src}")
            raise HTTPException(status_code=400, detail="File is empty")

        dest = SDF_DIR/src.name

        try:
            shutil.copy2(src, dest)
            logger.info(f"SDF copied for calculation: {src} -> {dest}. Selections: {data.selections}")
        except Exception as e:
            logger.error(f"Failed to copy file {src} -> {dest}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        return {"filename": src.name, "status": "success", "selections": data.selections}

    elif data.input_type == InputType.SMILES_FORMULA:
        if not data.smiles_formula:
            raise HTTPException(status_code=400, detail="SMILES/Formula is required")
        # Logic for SMILES/Formula would go here
        logger.info(f"Received SMILES/Formula: {data.smiles_formula}. Selections: {data.selections}")
        return {"status": "success", "input": data.smiles_formula, "selections": data.selections}

    elif data.input_type == InputType.SUSCEPTIBILITY:
        if data.susceptibility is None:
            raise HTTPException(status_code=400, detail="Susceptibility value is required")
        # Logic for user provided susceptibility would go here
        logger.info(f"Received susceptibility: {data.susceptibility}. Selections: {data.selections}")
        return {"status": "success", "value": data.susceptibility, "selections": data.selections}

    raise HTTPException(status_code=400, detail="Invalid input type")
