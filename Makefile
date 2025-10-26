SHELL := /bin/sh
.ONESHELL:
.SILENT:

BACKEND_APP_NAME   := backend_app

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

build-frontend:
	@rm -rf build/frontend build/app
	@npm ci --prefix frontend
	@npm run build-angular --prefix frontend
	@cd frontend && npx electron-builder --mac

dev:
	@npm run dev --prefix frontend

run:
	@"build/app/mac-arm64/Mag Bridge.app/Contents/MacOS/Mag Bridge"

logs:
	@tail -f ~/magbridge_runtime.log