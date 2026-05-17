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

# codebase-memory-mcp v0.6.1 — built from source with UI assets embedded
# UI variant requires Node.js (for graph-ui frontend build) + zlib (C linker).
# Node.js is installed temporarily and removed after the build; the devcontainer
# Node 22 feature installs its own copy later with no conflict.
# The resulting binary is fully static — no GLIBC constraint.
RUN apt-get update && \
    apt-get install -y --no-install-recommends zlib1g-dev && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    git clone --depth=1 --branch v0.6.1 \
        https://github.com/DeusData/codebase-memory-mcp.git /tmp/cbm-src && \
    cd /tmp/cbm-src && bash scripts/build.sh --with-ui && \
    install -m 755 build/c/codebase-memory-mcp /usr/local/bin/codebase-memory-mcp && \
    cd / && rm -rf /tmp/cbm-src && \
    apt-get remove -y nodejs npm && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.npm

USER ${USERNAME}