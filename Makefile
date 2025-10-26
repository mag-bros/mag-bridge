# Makefile — PyInstaller build from top level
# Project layout:
#   backend/
#     ├── main.py     # entry point
#     └── routes.py   # imported by main.py

SHELL := /bin/sh
.ONESHELL:
.SILENT:

# ---- Config -------------------------------------------------
APP_NAME   := app
SRC_DIR    := backend
ENTRY      := $(SRC_DIR)/main.py

# Output locations (all under ./build)
DIST_DIR   := build
WORK_DIR   := $(DIST_DIR)/.pyi-work
SPEC_DIR   := $(DIST_DIR)/.pyi-spec

PYI        := pyinstaller
# Common flags: onefile bundle, include backend on sys.path, and push all outputs into build/
PYI_FLAGS  := --onefile \
              --name $(APP_NAME) \
              --paths $(SRC_DIR) \
              --distpath $(DIST_DIR) \
              --workpath $(WORK_DIR) \
              --specpath $(SPEC_DIR) \
              --noconfirm

# OS specifics
ifeq ($(OS),Windows_NT)
  EXE := $(DIST_DIR)/$(APP_NAME).exe
else
  EXE := $(DIST_DIR)/$(APP_NAME)
endif

# ---- Targets ------------------------------------------------
.PHONY: help build run clean rebuild show-spec

help:
	echo "Targets:"
	echo "  build     - build one-file executable into $(DIST_DIR)/"
	echo "  run       - run the built binary"
	echo "  clean     - remove build outputs (incl. spec/work dirs)"
	echo "  rebuild   - clean + build"
	echo "  show-spec - print path to generated .spec"

build: clean
	mkdir -p "$(DIST_DIR)" "$(WORK_DIR)" "$(SPEC_DIR)"
	$(PYI) $(PYI_FLAGS) "$(ENTRY)"
	[ -f "$(EXE)" ] && echo "Built: $(EXE)" || (echo "Build failed"; exit 1)

run: build
	"$(EXE)"

clean:
	rm -rf "$(DIST_DIR)"

rebuild: clean build

show-spec:
	ls -1 "$(SPEC_DIR)"/*.spec 2>/dev/null || echo "No spec yet; run 'make build' first"
