"""Operational commands: run, logs, remove-quarantine."""
from __future__ import annotations

import platform
import subprocess
import sys

import click

from _env.config import PACKAGE_EXECUTABLE, LOG_DIR, LOG_FILE, PRODUCT_NAME
from _env.utils import cli, _echo_header, _echo_success, _echo_error, _echo_warn, _echo_info


@cli.command("run")
def run_app() -> None:
    """Run the packaged MagBridge app."""
    _echo_header("Running Packaged App")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    _echo_info(f"Launching: {PACKAGE_EXECUTABLE}")
    try:
        subprocess.run([str(PACKAGE_EXECUTABLE)], check=True)
    except FileNotFoundError:
        _echo_error(f"Executable not found: {PACKAGE_EXECUTABLE}")
        _echo_warn("Run 'python scripts/environment.py build' first")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        _echo_error(f"App exited with code {e.returncode}")
        sys.exit(e.returncode)


@cli.command()
def logs() -> None:
    """Tail app logs."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _echo_info(f"Tailing logs at: {LOG_FILE}")
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ["powershell", "-Command", f"Get-Content -Wait -Path '{LOG_FILE}'"],
                check=True,
            )
        else:
            subprocess.run(["tail", "-f", str(LOG_FILE)], check=True)
    except KeyboardInterrupt:
        click.echo("\n🛑 Log tailing stopped")


@cli.command("remove-quarantine")
@click.option(
    "--app",
    default=f"/Applications/{PRODUCT_NAME}.app",
    show_default=True,
    help="Path to the .app bundle",
)
def remove_quarantine(app: str) -> None:
    """Remove macOS quarantine attribute from the app bundle."""
    _echo_info(f"Removing quarantine from: {app}")
    result = subprocess.run(["sudo", "xattr", "-dr", "com.apple.quarantine", app])
    if result.returncode == 0:
        _echo_success("Quarantine attribute removed")
    else:
        _echo_error("Failed to remove quarantine attribute")
        sys.exit(result.returncode)
