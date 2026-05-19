"""Shared helpers: CLI group, output formatting, port management, env checks."""
from __future__ import annotations

import os
import platform
import signal
import subprocess
from pathlib import Path

import click

from _env.config import VENV_EXISTS

# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(version="1.0.0", prog_name="MagBridge Environment")
def cli() -> None:
    """MagBridge development environment manager."""
    pass


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _echo_header(title: str) -> None:
    click.echo(f"\n🚀 {click.style(title, fg='cyan', bold=True)}\n")


def _echo_success(msg: str) -> None:
    click.echo(f"✅ {msg}")


def _echo_error(msg: str) -> None:
    click.echo(f"❌ {click.style(msg, fg='red')}", err=True)


def _echo_warn(msg: str) -> None:
    click.echo(f"⚠️  {click.style(msg, fg='yellow')}")


def _echo_info(msg: str) -> None:
    click.echo(f"📦 {msg}")


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------


def _kill_port(port: int) -> bool:
    """Kill process listening on *port*. Returns True if anything was killed."""
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
            )
            killed = False
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if parts:
                        subprocess.run(
                            ["taskkill", "/F", "/PID", parts[-1]],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        killed = True
            return killed
        except Exception:
            return False

    # Unix: lsof → fuser fallback
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            for pid in result.stdout.strip().split("\n"):
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except (ProcessLookupError, ValueError):
                    pass
            return True
    except FileNotFoundError:
        subprocess.run(
            f"fuser -k {port}/tcp",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    return False


# ---------------------------------------------------------------------------
# Environment checks
# ---------------------------------------------------------------------------


def _check_venv() -> bool:
    """Return False (with error message) if the project venv is absent."""
    if not VENV_EXISTS:
        _echo_error("Virtual environment not found!")
        click.echo("   Run: uv venv .venv && uv pip install -r requirements.txt")
        return False
    return True


def _check_node_modules(path: Path, name: str) -> bool:
    """Auto-install node_modules if missing. Returns False on failure."""
    node_modules = path / "node_modules"
    if not node_modules.exists():
        _echo_info(f"Installing {name} dependencies...")
        result = subprocess.run(["npm", "install"], cwd=path)
        if result.returncode != 0:
            _echo_error(f"Failed to install {name} dependencies")
            return False
    return True
