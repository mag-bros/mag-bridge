"""Build and packaging commands: build-backend, build, info, clean."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import click

from _env.config import (
    BACKEND_APPNAME,
    BACKEND_ENTRYPOINT,
    BACKEND_SRC,
    BACKEND_TARGET,
    BUILD_DIR,
    EB_PLATFORM,
    ELECTRON,
    FRONTEND,
    FRONTEND_TARGET,
    LOG_DIR,
    LOG_FILE,
    PACKAGE_EXECUTABLE,
    PACKAGE_TARGET,
    PORT_ANGULAR,
    PORT_BACKEND,
    PRODUCT_NAME,
    ROOT,
)
from _env.utils import _echo_error, _echo_header, _echo_info, _echo_success, _echo_warn, _node_bin, cli

# ---------------------------------------------------------------------------
# Internal helper (shared by build-backend and build)
# ---------------------------------------------------------------------------


def _run_build_backend() -> None:
    """Build backend with PyInstaller.

    Uses sys.executable so it works both in a venv (local dev) and with a
    system Python (CI) — as long as the script is invoked with the right
    interpreter.
    """
    if BACKEND_TARGET.exists():
        shutil.rmtree(BACKEND_TARGET)
    for d in [BACKEND_TARGET, BACKEND_TARGET / ".pyi-work", BACKEND_TARGET / ".pyi-specs"]:
        d.mkdir(parents=True, exist_ok=True)

    _echo_info(f"Building backend with PyInstaller → {BACKEND_TARGET}")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name",
            BACKEND_APPNAME,
            "--paths",
            str(BACKEND_SRC),
            "--distpath",
            str(BACKEND_TARGET),
            "--workpath",
            str(BACKEND_TARGET / ".pyi-work"),
            "--specpath",
            str(BACKEND_TARGET / ".pyi-specs"),
            "--noconfirm",
            str(BACKEND_ENTRYPOINT),
        ],
        cwd=ROOT,
    )
    if result.returncode == 0:
        _echo_success(f"Backend packaged: {BACKEND_TARGET}/{BACKEND_APPNAME}")
    else:
        _echo_error("Failed to package backend")
        sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@cli.command("build-backend")
def build_backend() -> None:
    """Build backend with PyInstaller."""
    _echo_header("Building Backend")
    _run_build_backend()


@cli.command()
@click.option("--platform", "eb_platform", default=None, help="Electron builder platform flag (--mac, --win, --linux)")
@click.option("--extra", "eb_extra", default="", help="Extra electron-builder flags")
def build(eb_platform: str | None, eb_extra: str) -> None:
    """Build full app: backend + Angular + Electron packaging."""
    _echo_header("Building MagBridge Full Stack")

    platform_flag = eb_platform or EB_PLATFORM

    # 1. Backend
    _run_build_backend()

    # 2. Clean frontend / package targets
    for target in [FRONTEND_TARGET, PACKAGE_TARGET]:
        if target.exists():
            shutil.rmtree(target)

    # 3. Angular
    _echo_info("Installing frontend deps (npm ci)...")
    subprocess.run([_node_bin("npm"), "ci"], cwd=FRONTEND, check=True)
    _echo_info("Building Angular...")
    subprocess.run([_node_bin("npm"), "run", "build:prod"], cwd=FRONTEND, check=True)

    # 4. Electron
    _echo_info("Installing Electron deps (npm ci)...")
    r = subprocess.run([_node_bin("npm"), "ci"], cwd=ELECTRON)
    if r.returncode != 0:
        _echo_warn("Electron deps skipped (run 'cd electron && npm ci' on host)")

    _echo_info(f"Packaging Electron ({platform_flag})...")
    cmd = [_node_bin("npx"), "electron-builder", platform_flag]
    if eb_extra:
        cmd.extend(eb_extra.split())
    r = subprocess.run(cmd, cwd=ELECTRON)
    if r.returncode == 0:
        _echo_success(f"Electron packaged under {PACKAGE_TARGET}")
    else:
        _echo_error("Failed to package Electron (run on host if needed)")
        sys.exit(r.returncode)


@cli.command()
def info() -> None:
    """Print configuration info."""
    _echo_header("MagBridge Configuration")
    rows = [
        ("ROOT_DIR", ROOT),
        ("HOME_DIR", Path.home()),
        ("BUILD_DIR", BUILD_DIR),
        ("PACKAGE_TARGET", PACKAGE_TARGET),
        ("PRODUCT_NAME", PRODUCT_NAME),
        ("FRONTEND_SRC", FRONTEND),
        ("FRONTEND_TARGET", FRONTEND_TARGET),
        ("ELECTRON_SRC", ELECTRON),
        ("BACKEND_APPNAME", BACKEND_APPNAME),
        ("BACKEND_SRC", BACKEND_SRC),
        ("BACKEND_TARGET", BACKEND_TARGET),
        ("BACKEND_ENTRYPOINT", BACKEND_ENTRYPOINT),
        ("LOG_DIR", LOG_DIR),
        ("LOG_FILE", LOG_FILE),
        ("PACKAGE_EXECUTABLE", PACKAGE_EXECUTABLE),
        ("EB_PLATFORM", EB_PLATFORM),
        ("PORT_ANGULAR", PORT_ANGULAR),
        ("PORT_BACKEND", PORT_BACKEND),
    ]
    for key, val in rows:
        click.echo(f"   {click.style(key, bold=True):<30} = {val}")


@cli.command()
def clean() -> None:
    """Clean build outputs."""
    _echo_header("Cleaning Build Outputs")
    for target in [BACKEND_TARGET, FRONTEND_TARGET, PACKAGE_TARGET]:
        if target.exists():
            shutil.rmtree(target)
            _echo_success(f"Removed {target}")
        else:
            click.echo(f"   (already clean) {target}")
