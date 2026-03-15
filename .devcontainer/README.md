## Base Architecture
* **Image:** `docker.io/library/python:3.12-slim-bookworm`
* **Profile:** Provides a highly secure, minimal-footprint OS foundation. Because it is a "slim" variant, it deliberately excludes non-essential system utilities and runtimes to reduce attack surface and build time.

## Core Features
* **Python:** Lightning-fast virtual environments and dependency management via `uv`.
* **Node.js:** Provisioned purely to make the binary and package manager available to the user, as the slim Python base image does not include it by default. 
* **Shell Experience:** ZSH out-of-the-box with Powerlevel10k, persistent history, and custom `dotfiles/.shell_utils` aliases.

## AI Isolation Security
Enforces a zero-trust execution sandbox for AI agents through strict cgroups, read-only kernel parameters, restricted namespace visibility, and non-root user isolation.

# Dev Container Lifecycle Architecture

This document outlines the chronological execution of our Dev Container setup. The architecture strictly separates OS-level dependencies, heavy project dependencies, and lightweight user customizations to enable CI/CD pre-building and guarantee a zero-wait Developer Experience (DX).

## The Execution Timeline

**1. Image Build (`Dockerfile`)**
* **Trigger:** `docker build`
* **Context:** Executes before the container exists.
* **Purpose:** Installs immutable, system-wide OS dependencies (e.g., `apt-get install`). This layer is baked into the Docker image cache.

**2. Container Instantiation (`docker run`)**
* **Trigger:** IDE requests the container environment.
* **Context:** The container starts, and the host OS mounts the local workspace (source code) into it.

**3. Workspace Dependencies (`updateContentCommand`)**
* **Trigger:** Runs **inside** the running container automatically.
* **Context:** Background process (blocks IDE terminal access).
* **Purpose:** Uses the container's isolated tools to download heavy project requirements (e.g., `npm install`, `uv venv`). *Note: In cloud environments like GitHub Codespaces, pre-builds pause and cache the state at this exact step.*

**4. User Customization (`postCreateCommand`)**
* **Trigger:** Runs **inside** the running container immediately after Step 3.
* **Context:** Background process (blocks IDE terminal access).
* **Purpose:** Installs fast, user-specific runtime configurations, dotfiles, and shell themes (e.g., Powerlevel10k, Git aliases).

**5. IDE Attachment**
* **Trigger:** VS Code Server completes its connection.
* **Context:** The terminal window opens for the developer.
* **Purpose:** The environment is 100% fully configured and ready for immediate interaction.

**6. Service Wake-up (`postStartCommand`)** *[Optional]*
* **Trigger:** Runs **inside** the container *every* time it wakes up from a stopped state (e.g., reopening a laptop).
* **Context:** Background process.
* **Purpose:** Starts background application services (e.g., FastAPI, Angular dev server).