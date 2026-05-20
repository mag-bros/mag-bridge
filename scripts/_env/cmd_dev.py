"""Dev server commands: fullstack, frontend, backend, electron, stop."""
from __future__ import annotations

import os
import platform
import signal
import subprocess
import sys
import time
from typing import NoReturn

import click

from _env.config import FRONTEND, ELECTRON, ROOT, VENV_PYTHON, PORT_ANGULAR, PORT_BACKEND
from _env.utils import (
    cli,
    _echo_header, _echo_success, _echo_error, _echo_warn,
    _kill_port, _check_venv, _check_node_modules,
)


@cli.command()
@click.option("--skip-install", is_flag=True, help="Skip npm install check")
def fullstack(skip_install: bool) -> NoReturn:
    """Start Angular + FastAPI backend (runs in container)."""
    _echo_header("Starting MagBridge Full Stack Development Mode")

    click.echo("📦 Services:")
    click.echo(f"   - Angular dev server (port {PORT_ANGULAR})")
    click.echo(f"   - FastAPI backend (port {PORT_BACKEND})")
    click.echo()

    if not _check_venv():
        sys.exit(1)
    if not skip_install and not _check_node_modules(FRONTEND, "Angular"):
        sys.exit(1)

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

    click.echo(f"🔧 Starting Backend on http://0.0.0.0:{PORT_BACKEND}...")
    env = os.environ.copy()
    env["NODE_ENV"] = "development"
    backend_proc = subprocess.Popen(
        [str(VENV_PYTHON), "-m", "uvicorn", "backend:app",
         "--reload", "--host", "0.0.0.0", "--port", str(PORT_BACKEND)],
        cwd=ROOT,
        env=env,
    )
    processes.append(backend_proc)
    time.sleep(2)

    click.echo(f"🎨 Starting Angular on http://0.0.0.0:{PORT_ANGULAR}...")
    angular_proc = subprocess.Popen(["npm", "run", "serve-reloader"], cwd=FRONTEND)
    processes.append(angular_proc)

    click.echo()
    _echo_success("Services started!")
    click.echo(f"   📡 Backend:  http://localhost:{PORT_BACKEND} (PID: {backend_proc.pid})")
    click.echo(f"   📡 API Docs: http://localhost:{PORT_BACKEND}/docs")
    click.echo(f"   🌐 Angular:  http://localhost:{PORT_ANGULAR} (PID: {angular_proc.pid})")
    click.echo()
    _echo_warn("Press Ctrl+C to stop all services")
    click.echo()

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
            [str(VENV_PYTHON), "-m", "uvicorn", "backend:app",
             "--reload", "--host", "0.0.0.0", "--port", str(PORT_BACKEND)],
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
    """Start Electron (run on the HOST machine outside the container)."""
    _echo_header("Starting Electron Development Mode")

    _echo_warn("Prerequisites:")
    click.echo("   1. Dev container must be running")
    click.echo(f"   2. Angular dev server must be running on port {PORT_ANGULAR}")
    click.echo(f"   3. Backend must be running on port {PORT_BACKEND}")
    click.echo()

    if not _check_node_modules(ELECTRON, "Electron"):
        sys.exit(1)

    # macOS Gatekeeper quarantines npm-downloaded binaries (ENOEXEC / errno -8).
    # Strip the attribute from the entire dist/ folder (works regardless of
    # exact binary path inside it).
    if platform.system() == "Darwin":
        electron_dist = ELECTRON / "node_modules" / "electron" / "dist"
        if electron_dist.exists():
            _echo_info("Removing macOS quarantine from Electron binary...")
            subprocess.run(
                ["xattr", "-dr", "com.apple.quarantine", str(electron_dist)],
                stderr=subprocess.DEVNULL,
            )

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
