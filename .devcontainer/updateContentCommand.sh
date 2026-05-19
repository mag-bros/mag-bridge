#!/bin/bash
set -euo pipefail

echo "[updateContentCommand]:: Starting Background Dependency Installation..."

# ------------------------------------------------------
# 1. ENVIRONMENT INFRASTRUCTURE SETUP
# ------------------------------------------------------
if [ ! -d ".venv" ]; then
	echo "[updateContentCommand]:: Creating fresh Linux-native virtual environment..."
	uv venv --clear --seed .venv
else
	echo "[updateContentCommand]:: Virtual environment exists."
fi

# ------------------------------------------------------
# 2. APPLICATION DEPENDENCY INSTALLATION
# ------------------------------------------------------
# Devcontainer Tooling Dependencies — Claude Code CLI, Promptfoo, Repomix.
# Kept under .devcontainer/ so devcontainer tooling stays separate from app code.
# PATH in devcontainer.json points at .devcontainer/node_modules/.bin so the
# binaries are reachable without `npx`.
if [ ! -d ".devcontainer/node_modules" ]; then
	echo "[updateContentCommand]:: Installing devcontainer tooling (claude, promptfoo, repomix)..."
	(cd .devcontainer && npm install)
else
	echo "[updateContentCommand]:: .devcontainer/node_modules exists. Skipping."
fi

# Python Dependencies
echo "[updateContentCommand]:: Installing Python requirements via uv..."
uv pip install -r requirements.txt -r requirements-ci.txt
