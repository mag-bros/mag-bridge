# Commands
SHELL := /bin/bash
PYTHON ?= python
NPM ?= npm
NPX ?= npx

.ONESHELL:
.SILENT:

# Project root paths (auto-detected to the directory containing this Makefile)
ROOT_DIR ?= $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
HOME_DIR ?= $(HOME)

# Frontend packaging
PRODUCT_NAME ?= MagBridge
FRONTEND_SRC ?= $(ROOT_DIR)/frontend
FRONTEND_TARGET := $(BUILD_DIR)/frontend

# Backend packaging
BACKEND_APPNAME ?= backend_app
BACKEND_SRC ?= $(ROOT_DIR)/backend
BACKEND_TARGET := $(BUILD_DIR)/backend
BACKEND_ENTRYPOINT ?= $(BACKEND_SRC)/main.py

# Build packaging
BUILD_DIR ?= $(ROOT_DIR)/frontend/build
PACKAGE_TARGET := $(BUILD_DIR)/app
PACKAGE_EXECUTABLE ?= $(PACKAGE_TARGET)/mac-arm64/$(PRODUCT_NAME).app/Contents/MacOS/$(PRODUCT_NAME)

# App logs
LOG_DIR ?= $(HOME_DIR)/magbridge
LOG_FILE ?= $(LOG_DIR)/app.log

# OS detection (GNU Make on Windows sets OS=Windows_NT)
EB_PLATFORM ?= --mac
EB_EXTRA ?=
ifeq ($(OS),Windows_NT)
  RM := rm -rf
  MKDIR := mkdir -p
  PATH_SEP := ;
  EB_PLATFORM = --win
	PACKAGE_EXECUTABLE = TODO_SET_THIS_VALUE_ON_WINDOWS
  PYTHON ?= python
else
  RM := rm -rf
  MKDIR := mkdir -p
  PATH_SEP := :
endif

.PHONY: build build-backend dev backend run logs info  clean

build-backend:
	$(RM) "$(BACKEND_TARGET)"
	$(MKDIR) "$(BACKEND_TARGET)" "$(BACKEND_TARGET)/.pyi-work" "$(BACKEND_TARGET)/.pyi-specs"
	@echo "⧗ Building backend with PyInstaller → $(BACKEND_TARGET)"
	$(PYTHON) -m PyInstaller $(PYINSTALLER_OPTS) \
	  --onefile \
	  --name "$(BACKEND_APPNAME)" \
	  --paths "$(BACKEND_SRC)" \
	  --distpath "$(BACKEND_TARGET)" \
	  --workpath "$(BACKEND_TARGET)/.pyi-work" \
	  --specpath "$(BACKEND_TARGET)/.pyi-specs" \
	  --noconfirm "$(BACKEND_ENTRYPOINT)"
	@echo "✓ Backend built: $(BACKEND_TARGET)/$(BACKEND_APPNAME) (or .exe on Windows)"

build: build-backend
	$(RM) "$(FRONTEND_TARGET)" "$(PACKAGE_TARGET)"
	@echo "⧗ Installing frontend deps"
	$(NPM) ci --prefix "$(FRONTEND_SRC)"
	@echo "⧗ Building Angular"
	$(NPM) run build-angular --prefix "$(FRONTEND_SRC)"
	@echo "⧗ Packaging Electron ($(EB_PLATFORM) $(EB_EXTRA))"
	cd "$(FRONTEND_SRC)" && $(NPX) electron-builder $(EB_PLATFORM) $(EB_EXTRA) && \
	  echo "✓ Frontend packaged under $(PACKAGE_TARGET)"

##### ------------
##### Dev & Run
##### ------------

dev:
	$(MKDIR) "$(LOG_DIR)"
	-rm -f "$(LOG_FILE)"
	@echo "⧗ Starting developer mode (Running Frontend with Backend) (logs: $(LOG_FILE))"
	$(NPM) run dev --prefix "$(FRONTEND_SRC)"

backend:
	@echo "⧗ Starting Backend (logs: $(LOG_FILE))"
	$(NPM) run dev-backend --prefix "$(FRONTEND_SRC)"

run:
	$(MKDIR) "$(LOG_DIR)"
	-rm -f "$(LOG_FILE)"
	@echo "⧗ Running packaged app: $(PACKAGE_EXECUTABLE)"
	"$(PACKAGE_EXECUTABLE)"

logs:
	$(MKDIR) "$(LOG_DIR)"
	@echo "⧗ Tailing logs at: $(LOG_FILE)"
	tail -f "$(LOG_FILE)"

info:
	@echo "------ Commands ------"
	@echo "SHELL    	= $(SHELL)"
	@echo "PYTHON   	= $(PYTHON)"
	@echo "NPM      	= $(NPM)"
	@echo "------ Project root paths  ------"
	@echo "ROOT_DIR        	= $(ROOT_DIR)"
	@echo "HOME_DIR        	= $(HOME_DIR)"
	@echo "------ Frontend packaging ------"
	@echo "PRODUCT_NAME    	= $(PRODUCT_NAME)"
	@echo "FRONTEND_SRC 		= $(FRONTEND_SRC)"
	@echo "FRONTEND_TARGET 	= $(FRONTEND_TARGET)"
	@echo "------ Backend packaging ------"
	@echo "BACKEND_APPNAME 	= $(BACKEND_APPNAME)"
	@echo "BACKEND_SRC  		= $(BACKEND_SRC)"
	@echo "BACKEND_TARGET  	= $(BACKEND_TARGET)"
	@echo "BACKEND_ENTRYPOINT      = $(BACKEND_ENTRYPOINT)"
	@echo "------ Build packaging ------"
	@echo "BUILD_DIR 		= $(BUILD_DIR)"
	@echo "PACKAGE_TARGET		= $(PACKAGE_TARGET)"
	@echo "------ App logs ------"
	@echo "LOG_DIR         	= $(LOG_DIR)"
	@echo "LOG_FILE        	= $(LOG_FILE)"
	@echo "------ OS detection ------"
	@echo "PACKAGE_EXECUTABLE	= $(PACKAGE_EXECUTABLE)"
	@echo "EB_PLATFORM     	= $(EB_PLATFORM)"
	@echo "PATH_SEP        	= $(PATH_SEP)"
	@echo "EB_EXTRA     	 	= $(EB_EXTRA)"

clean:
	@echo "⧗ Cleaning build outputs"
	$(RM) "$(BACKEND_TARGET)" "$(FRONTEND_TARGET)" "$(PACKAGE_TARGET)"
