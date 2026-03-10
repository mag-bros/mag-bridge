"""Venv pre-check — ensures active Python is in the project's .venv/."""
from __future__ import annotations

import sys
from pathlib import Path


class VenvCheckError(RuntimeError):
    pass


def check_venv(project_root: Path | None = None) -> None:
    """Raise VenvCheckError if sys.executable is not inside project_root/.venv/.

    Args:
        project_root: Project root directory. Defaults to cwd.
    """
    if project_root is None:
        project_root = Path.cwd()

    venv_dir = (project_root / ".venv").resolve()
    executable = Path(sys.executable).resolve()

    if not str(executable).startswith(str(venv_dir) + "/"):
        raise VenvCheckError(
            f"Active Python ({executable}) is not inside the project venv ({venv_dir}).\n"
            f"Fix: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
        )
