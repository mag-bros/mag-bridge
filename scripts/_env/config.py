"""Resolved paths, ports and platform constants for the MagBridge environment."""
from __future__ import annotations

import platform
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
# __file__ is scripts/_env/config.py  →  .parent.parent.parent = project root
ROOT = Path(__file__).parent.parent.parent.resolve()
FRONTEND = ROOT / "frontend"
ELECTRON = ROOT / "electron"
BACKEND_SRC = ROOT / "backend"

_venv_python = (
    ROOT / ".venv" / "Scripts" / "python.exe"
    if platform.system() == "Windows"
    else ROOT / ".venv" / "bin" / "python"
)
VENV_PYTHON = _venv_python if _venv_python.exists() else Path(sys.executable)
VENV_EXISTS = _venv_python.exists()

# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------
PORT_ANGULAR = 4200
PORT_BACKEND = 8000

# ---------------------------------------------------------------------------
# Build paths
# ---------------------------------------------------------------------------
BUILD_DIR = FRONTEND / "build"
PACKAGE_TARGET = BUILD_DIR / "app"
FRONTEND_TARGET = BUILD_DIR / "frontend"
BACKEND_TARGET = BUILD_DIR / "backend"
BACKEND_ENTRYPOINT = BACKEND_SRC / "main.py"

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------
PRODUCT_NAME = "MagBridge"
BACKEND_APPNAME = "backend_app"

# ---------------------------------------------------------------------------
# App logs
# ---------------------------------------------------------------------------
LOG_DIR = Path.home() / "magbridge"
LOG_FILE = LOG_DIR / "app.log"

# ---------------------------------------------------------------------------
# Platform  (Electron builder target + packaged executable path)
# ---------------------------------------------------------------------------
_sys = platform.system()
EB_PLATFORM = "--win" if _sys == "Windows" else "--linux" if _sys == "Linux" else "--mac"

if _sys == "Windows":
    PACKAGE_EXECUTABLE = PACKAGE_TARGET / "win-unpacked" / f"{PRODUCT_NAME}.exe"
elif _sys == "Linux":
    PACKAGE_EXECUTABLE = PACKAGE_TARGET / "linux-unpacked" / PRODUCT_NAME
else:  # macOS
    PACKAGE_EXECUTABLE = (
        PACKAGE_TARGET / "mac-arm64" / f"{PRODUCT_NAME}.app"
        / "Contents" / "MacOS" / PRODUCT_NAME
    )
