#!/bin/bash
set -euo pipefail

USERNAME='vscode_server'
echo "[postCreateCommand]:: Starting Dev Container Post-Create Setup..."

# ------------------------------------------------------
# 3. SHELL CUSTOMIZATION AND PERSISTENCE
# ------------------------------------------------------

# User-Space Runtime Dependencies (Powerlevel10k)
echo "[postCreateCommand]:: Installing Powerlevel10k theme..."
P10K_DIR="${HOME}/powerlevel10k"
P10K_VERSION="v1.20.0"
if [ ! -d "${P10K_DIR}" ]; then
	git clone --depth=1 --branch "${P10K_VERSION}" https://github.com/romkatv/powerlevel10k.git "${P10K_DIR}"
fi

# Persistent Command History Configuration
echo "[postCreateCommand]:: Configuring persistent Zsh history..."
sudo chown -R ${USERNAME} /commandhistory
if ! grep -q "SAVEHIST" "${HOME}/.zshrc"; then
	echo "export HISTFILE=/commandhistory/.zsh_history" >>"${HOME}/.zshrc"
	echo "export HISTSIZE=10000" >>"${HOME}/.zshrc"
	echo "export SAVEHIST=10000" >>"${HOME}/.zshrc"
	echo "setopt appendhistory" >>"${HOME}/.zshrc"
fi

# Shell Alias Injection (Bash and Zsh)
if [[ -f ".devcontainer/dotfiles/.shell_utils" ]]; then
	grep -q "alias uvpipr" "${HOME}/.bashrc" || cat ".devcontainer/dotfiles/.shell_utils" >>"${HOME}/.bashrc"
	grep -q "alias uvpipr" "${HOME}/.zshrc" || cat ".devcontainer/dotfiles/.shell_utils" >>"${HOME}/.zshrc"
	echo "[postCreateCommand]:: Aliases verified/injected successfully."
fi

# ------------------------------------------------------
# 4. CLAUDE CODE PLUGIN (magbridge-ai)
# ------------------------------------------------------
echo "[postCreateCommand]:: Setting up magbridge-ai Claude plugin..."
PLUGIN_REMOTE="https://github.com/mag-bros/magbridge-ai"
PLUGIN_PATH=".claude"

if [ -d "${PLUGIN_PATH}/.git" ]; then
    echo "[postCreateCommand]:: magbridge-ai found, syncing to latest..."
    git -C "${PLUGIN_PATH}" pull origin master 2>/dev/null || true
else
    echo "[postCreateCommand]:: Cloning magbridge-ai plugin..."
    git clone "${PLUGIN_REMOTE}" "${PLUGIN_PATH}"
    git -C "${PLUGIN_PATH}" checkout master
fi

PLUGIN_SHA=$(git -C "${PLUGIN_PATH}" rev-parse --short HEAD 2>/dev/null || echo "unknown")
echo "[postCreateCommand]:: magbridge-ai ready @ ${PLUGIN_SHA}."

echo "[postCreateCommand]:: Exit"
