FROM docker.io/library/python:3.12-slim-bookworm

ARG USERNAME=vscode_server
ARG USER_UID=6666
ARG USER_GID=6666

USER root

# Setup User and Permissions
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}

# Install OS Dependencies (Removed 'sudo' for strict AI Isolation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libxrender1 \
    libxext6 \
    libsm6 \
    libice6 \
    pulseaudio-utils \
    libfontconfig1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Claude persistent isolated auth
RUN mkdir -p /commandhistory /home/${USERNAME}/.claude \
    && chown -R ${USERNAME}:${USER_GID} /commandhistory /home/${USERNAME}/.claude

RUN pip install --no-cache-dir uv

# codebase-memory-mcp v0.6.1 — https://github.com/DeusData/codebase-memory-mcp/releases/tag/v0.6.1
RUN curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/c1eb3dd2d1285eb7b29e0c473e79e7a5a010bf20/install.sh \
    | bash -s -- --dir /usr/local/bin --skip-config

USER ${USERNAME}