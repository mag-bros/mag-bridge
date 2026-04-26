from pathlib import Path
import os
from fastapi import HTTPException

# APP_DATA_DIR: Use environment variable or default to project's data/sdf directory
# When running through Electron, this is set to user's home directory
# In development mode, defaults to project's data directory
_default_data_dir = Path(__file__).parent.parent / "data"
APP_DATA_DIR = Path(os.environ.get("APP_DATA_DIR", str(_default_data_dir))).resolve()

SDF_DIR = APP_DATA_DIR / "sdf"
SDF_DIR.mkdir(parents=True, exist_ok=True)

# Development mode detection
IS_DEV_MODE = os.environ.get("NODE_ENV") == "development"
WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()


def translate_path(path_str: str) -> Path:
    """
    Translate file path between host and container filesystems.
    
    Dev Mode (Electron on macOS + Backend in container):
        - Translates macOS workspace paths to container paths
        - /Users/*/mag-bridge/* → /workspaces/mag-bridge/*
        - Only allows files within workspace for security
        
    Prod Mode (Packaged app):
        - No translation, uses path as-is
        - Full system access
    
    Args:
        path_str: File path from Electron (macOS path in dev mode)
        
    Returns:
        Path object pointing to file in container (dev) or host (prod)
        
    Raises:
        HTTPException: If file not accessible in dev mode
    """
    if not IS_DEV_MODE:
        # Production mode: use path directly (Electron and backend on same system)
        return Path(path_str)
    
    # Development mode: translate macOS path to container path
    path = Path(path_str)
    
    # Try to find 'mag-bridge' in path components
    parts = path.parts
    try:
        # Find workspace root in path
        idx = None
        for i, part in enumerate(parts):
            if part == "mag-bridge":
                idx = i
                break
        
        if idx is None:
            raise ValueError("workspace_not_found")
        
        # Rebuild path from mag-bridge onwards
        # /Users/user/projects/mag-bridge/data/file.sdf → data/file.sdf
        relative_parts = parts[idx + 1:]
        if not relative_parts:
            raise ValueError("invalid_path")
            
        relative = Path(*relative_parts)
        container_path = WORKSPACE_ROOT / relative
        
        # Verify file exists in container
        if not container_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found in workspace: {relative}"
            )
        
        # Verify file is within workspace (security check)
        try:
            container_path.resolve().relative_to(WORKSPACE_ROOT)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Access denied: File outside workspace"
            )
        
        return container_path
        
    except ValueError as e:
        if str(e) == "workspace_not_found":
            raise HTTPException(
                status_code=400,
                detail="Dev mode: Please select file from workspace folder (e.g., mag-bridge/data/sdf/)"
            )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file path: {path_str}"
        )
