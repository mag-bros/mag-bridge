#!/usr/bin/env python3
"""
MagBridge Development Environment CLI

Run 'python scripts/environment.py --help' for all commands.

Internal structure:
    scripts/_env/config.py    — paths, ports, platform constants
    scripts/_env/utils.py     — shared helpers + Click group
    scripts/_env/cmd_dev.py   — dev server commands
    scripts/_env/cmd_build.py — build / packaging commands
    scripts/_env/cmd_npm.py   — npm dependency commands
    scripts/_env/cmd_ops.py   — run, logs, remove-quarantine
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts/ is on sys.path so the _env package is importable regardless
# of the working directory from which this script is invoked.
sys.path.insert(0, str(Path(__file__).parent))

from _env import cli  # noqa: E402

if __name__ == "__main__":
    cli()
