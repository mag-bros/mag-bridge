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
# Node.js Dependencies
if [ -f "package.json" ]; then
	if [ ! -d "node_modules" ]; then
		echo "[updateContentCommand]:: Installing Main App Node modules..."
		npm install
	else
		echo "[updateContentCommand]:: node_modules exists. Skipping npm install."
	fi
else
	echo "[updateContentCommand]:: No package.json found. Skipping npm install."
fi

# Python Dependencies
echo "[updateContentCommand]:: Installing Python requirements via uv..."
uv pip install -r requirements.txt -r requirements-ci.txt
