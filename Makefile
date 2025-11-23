SHELL := /bin/sh
.ONESHELL:
.SILENT:

##### ============
##### Core knobs (env-overridable): set via `make VAR=value` or export in shell
##### ============

# Project root (auto-detected to the directory containing this Makefile)
ROOT_DIR ?= $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

# Source directories
BACKEND_SRC ?= $(ROOT_DIR)/backend
FRONTEND_SRC ?= $(ROOT_DIR)/frontend

# Build output directories
BUILD ?= $(ROOT_DIR)/frontend/build
FRONTEND_DIST := $(BUILD)/frontend
BACKEND_DIST := $(BUILD)/backend
APP_DIST := $(BUILD)/app

# Backend packaging
BACKEND_APP_NAME ?= backend_app
BACKEND_ENTRY ?= $(BACKEND_SRC)/main.py
PYINSTALLER_OPTS ?= --onefile

# Frontend build
NPM ?= npm
NPX ?= npx
ELECTRON_BUILDER ?= $(NPX) electron-builder
# Target platform for electron-builder (override to --win, --linux, etc.)
EB_PLATFORM ?= --mac

# Logs
HOME_DIR ?= $(HOME)
LOG_DIR ?= $(HOME_DIR)/.magbridge/logs
LOG_FILE ?= $(LOG_DIR)/magbridge.log

# Runtime (packaged app) paths
APP_NAME ?= Mag Bridge
MAC_APP_BIN := $(APP_DIST)/mac-arm64/$(APP_NAME).app/Contents/MacOS/$(APP_NAME)

# Python (optionally point at your venv)
PYTHON ?= python3

# OS detection (GNU Make on Windows sets OS=Windows_NT)
ifeq ($(OS),Windows_NT)
  # Windows/MSYS/MinGW/WSL nuances
  RM := rm -rf
  MKDIR := mkdir -p
  PATH_SEP := ;
  EB_PLATFORM ?= --win
  PYTHON ?= python
else
  RM := rm -rf
  MKDIR := mkdir -p
  PATH_SEP := :
endif

##### ============
##### Phonies
##### ============

.PHONY: all clean build-backend build-frontend dev run logs show-vars

all: build-backend build-frontend

build-backend:
	$(RM) "$(BACKEND_DIST)"
	$(MKDIR) "$(BACKEND_DIST)" "$(BACKEND_DIST)/.pyi-work" "$(BACKEND_DIST)/.pyi-specs"
	@echo "⧗ Building backend with PyInstaller → $(BACKEND_DIST)"
	pyinstaller $(PYINSTALLER_OPTS) \
	  --name "$(BACKEND_APP_NAME)" \
	  --paths "$(BACKEND_SRC)" \
	  --distpath "$(BACKEND_DIST)" \
	  --workpath "$(BACKEND_DIST)/.pyi-work" \
	  --specpath "$(BACKEND_DIST)/.pyi-specs" \
	  --noconfirm "$(BACKEND_ENTRY)"
	@echo "✓ Backend built: $(BACKEND_DIST)/$(BACKEND_APP_NAME) (or .exe on Windows)"

build-app: build-backend
	$(RM) "$(FRONTEND_DIST)" "$(APP_DIST)"
	@echo "⧗ Installing frontend deps"
	$(NPM) ci --prefix "$(FRONTEND_SRC)"
	@echo "⧗ Building Angular"
	$(NPM) run build-angular --prefix "$(FRONTEND_SRC)"
	@echo "⧗ Packaging Electron ($(EB_PLATFORM))"
	cd "$(FRONTEND_SRC)" && $(NPX) electron-builder $(EB_PLATFORM)
	@echo "✓ Frontend packaged under $(APP_DIST)"

##### ============
##### Dev & Run
##### ============

# Dev: start front-end dev stack (your package.json 'dev' script). Keeps your current behavior.
dev:
	$(MKDIR) "$(LOG_DIR)"
	@rm $(LOG_FILE)
	@echo "⧗ Starting frontend dev (logs: $(LOG_FILE))"
	$(NPM) run dev --prefix "$(FRONTEND_SRC)"

# Run packaged app (mac default). Override MAC_APP_BIN or EB_PLATFORM as needed.
run:
	$(MKDIR) "$(LOG_DIR)"
	@rm $(LOG_FILE)
	@echo "⧗ Running packaged app: $(MAC_APP_BIN)"
	"$(MAC_APP_BIN)"

logs:
	$(MKDIR) "$(LOG_DIR)"
	@echo "⧗ Tailing logs at: $(LOG_FILE)"
	tail -f "$(LOG_FILE)"

show-vars:
	@echo "ROOT_DIR        = $(ROOT_DIR)"
	@echo "BACKEND_SRC     = $(BACKEND_SRC)"
	@echo "FRONTEND_SRC    = $(FRONTEND_SRC)"
	@echo "BUILD           = $(BUILD)"
	@echo "BACKEND_APP_NAME= $(BACKEND_APP_NAME)"
	@echo "BACKEND_ENTRY   = $(BACKEND_ENTRY)"
	@echo "BACKEND_DIST    = $(BACKEND_DIST)"
	@echo "FRONTEND_DIST   = $(FRONTEND_DIST)"
	@echo "APP_DIST        = $(APP_DIST)"
	@echo "LOG_FILE        = $(LOG_FILE)"
	@echo "PYTHON          = $(PYTHON)"
	@echo "EB_PLATFORM     = $(EB_PLATFORM)"

##### ============
##### Clean
##### ============

clean:
	@echo "⧗ Cleaning build outputs"
	$(RM) "$(BACKEND_DIST)" "$(FRONTEND_DIST)" "$(APP_DIST)"
