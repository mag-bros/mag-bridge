# ============================================================
# Makefile.windows — Windows EXE Builder + Dev Utilities
# ============================================================

SHELL           := cmd.exe
.SHELLFLAGS     := /C

# ------------------------------------------------------------
# Configurable Variables
# ------------------------------------------------------------
ROOT_DIR        := $(abspath .)
BUILD_DIR       := $(ROOT_DIR)/build
SCRIPTS_DIR     := $(ROOT_DIR)/scripts
DEVKIT_DIR		:= $(ROOT_DIR)/DevKit
UTILS_DIR       := $(SCRIPTS_DIR)/utils
BUILD_WRAPPER   := $(SCRIPTS_DIR)/build_wrapper.ps1

INSTALL_SRC     := $(SCRIPTS_DIR)/install.ps1
UNINSTALL_SRC   := $(SCRIPTS_DIR)/uninstall.ps1

INSTALL_EXE     := $(BUILD_DIR)/Install.exe
UNINSTALL_EXE   := $(BUILD_DIR)/Uninstall.exe

TITLE           := MagBridge Dependencies Installer
DOTNET_PROJECT  := $(DEVKIT_DIR)/DevKit.csproj
CONFIG          := Debug

# ------------------------------------------------------------
# PowerShell Invocation Wrapper
# ------------------------------------------------------------
# Ensures every command runs with consistent policy and settings
POWERSHELL := powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command

# ------------------------------------------------------------
# Targets
# ------------------------------------------------------------
.PHONY: all install build-install uninstall build-uninstall clean \
        build-dotnet run-dotnet publish-dotnet info

build-install:
	@$(POWERSHELL) "& { & '$(BUILD_WRAPPER)' -OutDir '$(BUILD_DIR)' -InstallSript '$(INSTALL_SRC)' -Output '$(INSTALL_EXE)' -Title '$(TITLE)' }"

install:
	@$(POWERSHELL) "& { & '$(INSTALL_SRC)' }"

build-uninstall:
	@$(POWERSHELL) "& { & '$(BUILD_WRAPPER)' -OutDir '$(BUILD_DIR)' -InstallSript '$(UNINSTALL_SRC)' -Output '$(UNINSTALL_EXE)' -Title '$(TITLE)' }"

clean:
	@$(POWERSHELL) "& { if (Test-Path '$(OUT_DIR)') { Remove-Item -Recurse -Force '$(OUT_DIR)'; Write-Host 'Cleaned $(OUT_DIR)' } else { Write-Host 'Nothing to clean.' } }"

# ------------------------------------------------------------
# 🧩 Development Utilities — .NET Project Management
# ------------------------------------------------------------

run:
	@powershell -NoProfile -Command "dotnet clean '$(DOTNET_PROJECT)'"
	@powershell -NoProfile -Command "dotnet build '$(DOTNET_PROJECT)'"
	@powershell -NoProfile -Command "dotnet run --project '$(DOTNET_PROJECT)'"