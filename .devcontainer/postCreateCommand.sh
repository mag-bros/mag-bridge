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

echo "[postCreateCommand]:: Updating submodules..."
git submodule update --init --remote .claude

echo "[postCreateCommand]:: Exit"
