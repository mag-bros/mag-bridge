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
DEVKIT_DIR		:= $(ROOT_DIR)/MagBridge
UTILS_DIR       := $(SCRIPTS_DIR)/utils
BUILD_WRAPPER   := $(SCRIPTS_DIR)/build_wrapper.ps1

INSTALL_SRC     := $(SCRIPTS_DIR)/install.ps1
UNINSTALL_SRC   := $(SCRIPTS_DIR)/uninstall.ps1

INSTALL_EXE     := $(BUILD_DIR)/Install.exe
UNINSTALL_EXE   := $(BUILD_DIR)/Uninstall.exe

TITLE           := MagBridge Dependencies Installer
DOTNET_PROJECT  := $(DEVKIT_DIR)/MagBridge.csproj
CONFIG          := Debug

# ------------------------------------------------------------
# PowerShell Invocation Wrapper
# ------------------------------------------------------------
# Ensures every command runs with consistent policy and settings
POWERSHELL := powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command

# ------------------------------------------------------------
# Targets
# ------------------------------------------------------------
.PHONY: all build build-dotnet build-install build-uninstall clean info install publish-dotnet rebuild-dotnet run run-dotnet uninstall

build-install:
	@$(POWERSHELL) "& { & '$(BUILD_WRAPPER)' -OutDir '$(BUILD_DIR)' -InstallSript '$(INSTALL_SRC)' -Output '$(INSTALL_EXE)' -Title '$(TITLE)' }"

install:
	@$(POWERSHELL) "& { & '$(INSTALL_SRC)' }"

build-uninstall:
	@$(POWERSHELL) "& { & '$(BUILD_WRAPPER)' -OutDir '$(BUILD_DIR)' -InstallSript '$(UNINSTALL_SRC)' -Output '$(UNINSTALL_EXE)' -Title '$(TITLE)' }"

# ------------------------------------------------------------
# 🧩 Development Utilities — .NET Project Management
# ------------------------------------------------------------
APP_CONFIG  ?= ../Configs/sdk-installer.json
APP_LICENSE ?= ../Licenses/sdk-license.txt
APP_ICON    ?= ../Assets/sdk.ico
DOTNET_ARGS = -p:AppConfig=$(APP_CONFIG) \
              -p:AppLicense=$(APP_LICENSE) \
              -p:AppIcon=$(APP_ICON)

clean:
	@powershell -NoProfile -Command "dotnet clean '$(DOTNET_PROJECT)'"

build:
	@powershell -NoProfile -Command "dotnet build --nologo '$(DOTNET_PROJECT)'"

run: build
	@powershell -NoProfile -Command "dotnet run --no-build --project '$(DOTNET_PROJECT)'"
