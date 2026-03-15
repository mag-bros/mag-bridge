FROM docker.io/library/python:3.12-slim-bookworm

ARG USERNAME=vscode_server
ARG USER_UID=6666
ARG USER_GID=6666

# Setup User and Permissions
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}

# Install OS Dependencies (Removed 'sudo' for strict AI Isolation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Claude persistent isolated auth
RUN mkdir -p /commandhistory /home/${USERNAME}/.claude \
    && chown -R ${USERNAME}:${USER_GID} /commandhistory /home/${USERNAME}/.claude

RUN pip install --no-cache-dir uv

USER ${USERNAME}