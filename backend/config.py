from pathlib import Path
import os

APP_DATA_DIR = Path(os.environ["APP_DATA_DIR"]).resolve()

SDF_DIR = APP_DATA_DIR / "sdf"
SDF_DIR.mkdir(parents=True, exist_ok=True)
