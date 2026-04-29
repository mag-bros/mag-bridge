#!/usr/bin/env python3
"""
MagBridge Development Environment CLI

Usage:
    python scripts/environment.py fullstack   # Start Angular + Backend
    python scripts/environment.py frontend    # Start Angular only
    python scripts/environment.py backend     # Start Backend only
    python scripts/environment.py electron    # Start Electron (run on host)
    python scripts/environment.py stop        # Stop all services
    python scripts/environment.py install     # Install dependencies
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

import click

# Project paths
ROOT = Path(__file__).parent.parent.resolve()
FRONTEND = ROOT / "frontend"
ELECTRON = ROOT / "electron"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"

# Ports
PORT_ANGULAR = 4200
PORT_BACKEND = 8000


def _echo_header(title: str) -> None:
    """Print a styled header."""
    click.echo(f"\n🚀 {click.style(title, fg='cyan', bold=True)}\n")


def _echo_success(msg: str) -> None:
    click.echo(f"✅ {msg}")


def _echo_error(msg: str) -> None:
    click.echo(f"❌ {click.style(msg, fg='red')}", err=True)


def _echo_warn(msg: str) -> None:
    click.echo(f"⚠️  {click.style(msg, fg='yellow')}")


def _echo_info(msg: str) -> None:
    click.echo(f"📦 {msg}")


def _kill_port(port: int) -> bool:
    """Kill process on port. Returns True if a process was killed."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except (ProcessLookupError, ValueError):
                    pass
            return True
    except FileNotFoundError:
        # lsof not available, try fuser
        subprocess.run(
            f"fuser -k {port}/tcp",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
    return False


def _check_venv() -> bool:
    """Check if virtual environment exists."""
    if not VENV_PYTHON.exists():
        _echo_error("Virtual environment not found!")
        click.echo("   Run: uv venv .venv && uv pip install -r requirements.txt")
        return False
    return True


def _check_node_modules(path: Path, name: str) -> bool:
    """Check and install node_modules if needed."""
    node_modules = path / "node_modules"
    if not node_modules.exists():
        _echo_info(f"Installing {name} dependencies...")
        result = subprocess.run(["npm", "install"], cwd=path)
        if result.returncode != 0:
            _echo_error(f"Failed to install {name} dependencies")
            return False
    return True


@click.group()
@click.version_option(version="1.0.0", prog_name="MagBridge Environment")
def cli() -> None:
    """MagBridge development environment manager."""
    pass


@cli.command()
@click.option("--skip-install", is_flag=True, help="Skip npm install check")
def fullstack(skip_install: bool) -> NoReturn:
    """Start Angular + FastAPI backend (runs in container)."""
    _echo_header("Starting MagBridge Full Stack Development Mode")

    click.echo("📦 Services:")
    click.echo(f"   - Angular dev server (port {PORT_ANGULAR})")
    click.echo(f"   - FastAPI backend (port {PORT_BACKEND})")
    click.echo()

    # Checks
    if not _check_venv():
        sys.exit(1)

    if not skip_install:
        if not _check_node_modules(FRONTEND, "Angular"):
            sys.exit(1)

    # Kill existing processes
    click.echo("🧹 Cleaning up existing processes...")
    _kill_port(PORT_ANGULAR)
    _kill_port(PORT_BACKEND)

    processes: list[subprocess.Popen] = []

    def cleanup(signum: int | None = None, frame: object = None) -> NoReturn:
        click.echo("\n🛑 Stopping services...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            except Exception:
                pass
        _kill_port(PORT_ANGULAR)
        _kill_port(PORT_BACKEND)
        _echo_success("All services stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Start Backend
    click.echo(f"🔧 Starting Backend on http://0.0.0.0:{PORT_BACKEND}...")
    env = os.environ.copy()
    env["NODE_ENV"] = "development"
    backend_proc = subprocess.Popen(
        [
            str(VENV_PYTHON),
            "-m",
            "uvicorn",
            "backend:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            str(PORT_BACKEND),
        ],
        cwd=ROOT,
        env=env,
    )
    processes.append(backend_proc)

    # Wait for backend to start
    time.sleep(2)

    # Start Angular
    click.echo(f"🎨 Starting Angular on http://0.0.0.0:{PORT_ANGULAR}...")
    angular_proc = subprocess.Popen(
        ["npm", "run", "serve-reloader"],
        cwd=FRONTEND,
    )
    processes.append(angular_proc)

    click.echo()
    _echo_success("Services started!")
    click.echo(f"   📡 Backend:  http://localhost:{PORT_BACKEND} (PID: {backend_proc.pid})")
    click.echo(f"   📡 API Docs: http://localhost:{PORT_BACKEND}/docs")
    click.echo(f"   🌐 Angular:  http://localhost:{PORT_ANGULAR} (PID: {angular_proc.pid})")
    click.echo()
    _echo_warn("Press Ctrl+C to stop all services")
    click.echo()

    # Wait for processes
    try:
        while True:
            for proc in processes:
                if proc.poll() is not None:
                    _echo_error(f"Process {proc.pid} exited with code {proc.returncode}")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

    sys.exit(0)


@cli.command()
def frontend() -> NoReturn:
    """Start Angular dev server only."""
    _echo_header("Starting Angular Dev Server")

    if not _check_node_modules(FRONTEND, "Angular"):
        sys.exit(1)

    _kill_port(PORT_ANGULAR)

    click.echo(f"🎨 Starting Angular on http://0.0.0.0:{PORT_ANGULAR}...")
    try:
        subprocess.run(["npm", "run", "serve-reloader"], cwd=FRONTEND, check=True)
    except KeyboardInterrupt:
        click.echo("\n🛑 Angular stopped")
    except subprocess.CalledProcessError as e:
        _echo_error(f"Angular exited with code {e.returncode}")
        sys.exit(e.returncode)

    sys.exit(0)


@cli.command()
def backend() -> NoReturn:
    """Start FastAPI backend only."""
    _echo_header("Starting FastAPI Backend")

    if not _check_venv():
        sys.exit(1)

    _kill_port(PORT_BACKEND)

    click.echo(f"🔧 Starting Backend on http://0.0.0.0:{PORT_BACKEND}...")
    env = os.environ.copy()
    env["NODE_ENV"] = "development"
    try:
        subprocess.run(
            [
                str(VENV_PYTHON),
                "-m",
                "uvicorn",
                "backend:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                str(PORT_BACKEND),
            ],
            cwd=ROOT,
            env=env,
            check=True,
        )
    except KeyboardInterrupt:
        click.echo("\n🛑 Backend stopped")
    except subprocess.CalledProcessError as e:
        _echo_error(f"Backend exited with code {e.returncode}")
        sys.exit(e.returncode)

    sys.exit(0)


@cli.command()
def electron() -> NoReturn:
    """Start Electron (run on macOS host OUTSIDE container)."""
    _echo_header("Starting Electron Development Mode")

    _echo_warn("Prerequisites:")
    click.echo("   1. Dev container must be running")
    click.echo(f"   2. Angular dev server must be running on port {PORT_ANGULAR}")
    click.echo(f"   3. Backend must be running on port {PORT_BACKEND}")
    click.echo()

    if not _check_node_modules(ELECTRON, "Electron"):
        sys.exit(1)

    click.echo(f"⏳ Waiting for Angular dev server at http://localhost:{PORT_ANGULAR}...")
    try:
        subprocess.run(["npm", "run", "dev"], cwd=ELECTRON, check=True)
    except KeyboardInterrupt:
        click.echo("\n🛑 Electron stopped")
    except subprocess.CalledProcessError as e:
        _echo_error(f"Electron exited with code {e.returncode}")
        sys.exit(e.returncode)

    sys.exit(0)


@cli.command()
def stop() -> None:
    """Stop all development services."""
    _echo_header("Stopping Development Services")

    killed_angular = _kill_port(PORT_ANGULAR)
    killed_backend = _kill_port(PORT_BACKEND)

    if killed_angular:
        _echo_success(f"Killed process on port {PORT_ANGULAR} (Angular)")
    if killed_backend:
        _echo_success(f"Killed process on port {PORT_BACKEND} (Backend)")

    if not killed_angular and not killed_backend:
        click.echo("No services were running")
    else:
        _echo_success("All services stopped")


@cli.command()
@click.option("--frontend-only", is_flag=True, help="Install frontend deps only")
@click.option("--electron-only", is_flag=True, help="Install electron deps only")
def install(frontend_only: bool, electron_only: bool) -> None:
    """Install npm dependencies."""
    _echo_header("Installing Dependencies")

    if not frontend_only and not electron_only:
        # Install both
        _echo_info("Installing Frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=FRONTEND, check=True)
        _echo_warn("For Electron, run 'python scripts/environment.py install --electron-only' on macOS host")
    elif frontend_only:
        _echo_info("Installing Frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=FRONTEND, check=True)
    elif electron_only:
        _echo_info("Installing Electron dependencies...")
        subprocess.run(["npm", "install"], cwd=ELECTRON, check=True)

    _echo_success("Dependencies installed")


if __name__ == "__main__":
    cli()
