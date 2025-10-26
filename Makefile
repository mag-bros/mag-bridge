SHELL := /bin/sh
.ONESHELL:
.SILENT:

BACKEND_APP_NAME   := backend_app

ifeq ($(OS),Windows_NT)
  EXE := build/backend/$(BACKEND_APP_NAME).exe
else
  EXE := build/backend/$(BACKEND_APP_NAME)
endif

.PHONY: build-backend build-frontend

all: build-backend build-frontend

build-backend:
	@rm -rf build/backend
	@pyinstaller --onefile \
              --name $(BACKEND_APP_NAME) \
              --paths backend \
              --distpath build/backend \
              --workpath build/backend/.pyi-work \
              --specpath build/backend/.pyi-specs \
              --noconfirm backend/main.py
	@[ -f "$(EXE)" ] && echo "Built: $(EXE)" || (echo "Build failed"; exit 1)

build-frontend:
	@rm -rf build/frontend build/app
	@npm ci --prefix frontend
	@npm run build-angular --prefix frontend
	@cd frontend && NODE_ENV=release npx electron-builder --mac
