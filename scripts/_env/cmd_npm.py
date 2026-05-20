"""npm dependency management commands: install, npm-update, list-outdated, update-lock, rebuild-node."""

from __future__ import annotations

import shutil
import subprocess
import sys

import click

from _env.config import ELECTRON, FRONTEND
from _env.utils import _echo_error, _echo_header, _echo_info, _echo_success, _echo_warn, _node_bin, cli


@cli.command()
@click.option("--frontend-only", is_flag=True, help="Install frontend deps only")
@click.option("--electron-only", is_flag=True, help="Install electron deps only")
def install(frontend_only: bool, electron_only: bool) -> None:
    """Install npm dependencies."""
    _echo_header("Installing Dependencies")

    if not frontend_only and not electron_only:
        _echo_info("Installing Frontend dependencies...")
        subprocess.run([_node_bin("npm"), "install"], cwd=FRONTEND, check=True)
        _echo_warn("For Electron, run 'python scripts/environment.py install --electron-only' on the host machine")
    elif frontend_only:
        _echo_info("Installing Frontend dependencies...")
        subprocess.run([_node_bin("npm"), "install"], cwd=FRONTEND, check=True)
    elif electron_only:
        _echo_info("Installing Electron dependencies...")
        subprocess.run([_node_bin("npm"), "install"], cwd=ELECTRON, check=True)

    _echo_success("Dependencies installed")


@cli.command("npm-update")
def npm_update() -> None:
    """Update frontend npm dependencies via npm-check-updates."""
    _echo_header("Updating Frontend npm Dependencies")
    _echo_info("Checking for updates with npm-check-updates...")
    subprocess.run(
        [_node_bin("npm"), "exec", "npm-check-updates", "--", "--packageFile", "package.json", "--upgrade"],
        cwd=FRONTEND,
        check=True,
    )
    _echo_info("Installing updated dependencies...")
    result = subprocess.run([_node_bin("npm"), "install"], cwd=FRONTEND)
    if result.returncode == 0:
        _echo_success("npm dependencies updated")
    else:
        _echo_error("npm dependencies update FAILED")
        sys.exit(result.returncode)


@cli.command("list-outdated")
def list_outdated() -> None:
    """List outdated frontend npm dependencies."""
    subprocess.run([_node_bin("npm"), "outdated", "--long"], cwd=FRONTEND)


@cli.command("update-lock")
def update_lock() -> None:
    """Update frontend package-lock.json without installing."""
    _echo_info("Updating package-lock.json...")
    subprocess.run([_node_bin("npm"), "install", "--package-lock-only"], cwd=FRONTEND, check=True)
    _echo_success("package-lock.json updated")


@cli.command("rebuild-node")
def rebuild_node() -> None:
    """Reset frontend lockfile and reinstall node_modules."""
    _echo_header("Rebuilding Frontend Node Dependencies")
    lock = FRONTEND / "package-lock.json"
    modules = FRONTEND / "node_modules"

    _echo_info("Removing package-lock.json and node_modules...")
    if lock.exists():
        lock.unlink()
    if modules.exists():
        shutil.rmtree(modules)

    _echo_info("Installing dependencies from scratch...")
    result = subprocess.run([_node_bin("npm"), "install"], cwd=FRONTEND)
    if result.returncode == 0:
        _echo_success("Lockfile regenerated and dependencies reinstalled")
    else:
        _echo_error("Failed to reset lockfile or reinstall dependencies")
        sys.exit(result.returncode)
