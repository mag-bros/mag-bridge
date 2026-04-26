# MagBridge Electron (Sidecar)

Electron wrapper for MagBridge, designed to run **exclusively on the macOS host** while connecting to Angular and Backend running in the Dev Container.

## Architecture

```
┌─────────────────────────────────────┐
│  macOS Host                         │
│  ┌───────────────────────────────┐  │
│  │  Electron (this folder)       │  │
│  │  → Loads http://localhost:4200│  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              ↓ (port forwarding)
┌─────────────────────────────────────┐
│  Dev Container (Linux)              │
│  ┌───────────────────────────────┐  │
│  │  Angular Dev Server :4200     │  │
│  │  FastAPI Backend    :8000     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Requirements

- **Host OS:** macOS, Windows (10/11 with Docker Desktop), or Linux
- **Node.js 22+** installed on host
- Dev Container running with ports 4200 and 8000 forwarded

## Installation (First Time)

```bash
# On host (macOS/Windows/Linux), navigate to this folder
cd electron

# Install dependencies
npm install
```

## Development Mode

### 1. Start Dev Container Services (Inside Container)

```bash
# Terminal 1 (in Dev Container): Start Full Stack
make dev-fullstack
```

Or separately:
```bash
# Terminal 1 (in Dev Container): Start Angular dev server
cd frontend
npm run serve-reloader  # Runs on http://0.0.0.0:4200

# Terminal 2 (in Dev Container): Start Backend
make backend  # Runs on http://0.0.0.0:8000
```

### 2. Start Electron (On Host - Outside Container)

**macOS/Linux:**
```bash
cd electron
npm run dev
```

**Windows (PowerShell/CMD):**
```bash
cd electron
npm run dev
```

**What happens:**
- Electron waits for `http://localhost:4200` (or `host.docker.internal:4200` on Windows) to be available
- Opens Electron window loading Angular from dev server
- Both Electron and browser can access the same Angular app simultaneously
- Hot Module Reload (HMR) works for both

## Production Build

```bash
# On host (macOS/Windows/Linux)
cd /path/to/mag-bridge
make build
```

**This will:**
1. Build Angular → `frontend/build/frontend/`
2. Build Backend → `frontend/build/backend/`
3. Package Electron → `frontend/build/app/`

**Result:**
- **macOS:** `frontend/build/app/mac-arm64/MagBridge.app`
- **Windows:** `frontend/build/app/win-unpacked/MagBridge.exe`
- **Linux:** `frontend/build/app/MagBridge-0.0.0.AppImage`

## Configuration

All configuration is in `app-config.js`:

### Environment Variables

- `NODE_ENV` - `development` or `production`
- `MANAGE_BACKEND` - Set to `1` to let Electron manage backend process
- `BACKEND_CMD` - Python executable (default: `python3`)
- `BACKEND_CWD` - Working directory for backend (default: `../`)

### Development Mode Overrides

```bash
# Custom backend port
UVICORN_PORT=8080 npm run dev

# Disable backend management (use external backend)
MANAGE_BACKEND=0 npm run dev

# Custom Python path
BACKEND_CMD=/usr/local/bin/python3.12 npm run dev
```

## File Structure

```
electron/
├── package.json        # Electron dependencies (electron, electron-builder)
├── main.js            # Main process (window management, IPC)
├── preload.js         # Context bridge (security layer)
├── logging.js         # Unified logging system
├── app-config.js      # Configuration resolver
└── README.md          # This file
```

## Troubleshooting

### Electron can't connect to Angular

**Check:**
1. Angular dev server is running: `http://localhost:4200` in browser
2. Port 4200 is forwarded from container to host
3. No firewall blocking localhost connections

**Windows specific:**
- If `localhost:4200` doesn't work, Electron automatically tries `host.docker.internal:4200`
- Ensure Docker Desktop is running with WSL2 backend
- Check Docker Desktop → Settings → Resources → WSL Integration

### Backend not starting

**Check:**
1. `MANAGE_BACKEND=1` is set
2. Python virtual environment exists at `../.venv`
3. Backend dependencies installed: `uv pip install -r requirements.txt`

### Build fails on macOS

**Check:**
1. Xcode Command Line Tools installed: `xcode-select --install`
2. Node.js version: `node --version` (should be 22+)
3. Clean build: `rm -rf node_modules && npm install`

### Build fails on Windows

**Check:**
1. Node.js version: `node --version` (should be 22+)
2. Windows Build Tools: `npm install --global windows-build-tools` (if needed)
3. Clean build: `rmdir /s node_modules && npm install`

## Security

✅ **Implemented:**
- `contextIsolation: true` - Renderer process isolated from Node.js
- `nodeIntegration: false` - No direct Node.js access in renderer
- Context Bridge API - Secure IPC communication via `window.electronAPI`

## Logs

Development logs:
```bash
tail -f ~/magbridge-dev/app.log
```

Production logs:
```bash
tail -f ~/magbridge/app.log
```

## Related Documentation

- [Dev Container Setup](../.devcontainer/README.md)
- [Frontend (Angular)](../frontend/README.md)
- [Makefile Commands](../Makefile)
