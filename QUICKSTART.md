# 🚀 Quick Start Guide - Electron Sidecar Architecture

## Architecture Overview

MagBridge now uses a **sidecar architecture** where Electron runs on the macOS host while Angular and Backend run in a Dev Container:

```
┌─────────────────────────────────────┐
│  macOS Host                         │
│  ┌───────────────────────────────┐  │
│  │  Electron (electron/)         │  │
│  │  Port: Loads localhost:4200   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              ↓ (port forwarding)
┌─────────────────────────────────────┐
│  Dev Container (Linux)              │
│  ┌───────────────────────────────┐  │
│  │  Angular :4200                │  │
│  │  Backend :8000                │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Development Workflow

### Option 1: Browser Only (Inside Container)

Perfect for pure Angular development:

```bash
# Terminal 1: Start Angular dev server
cd frontend
npm run serve-reloader

# Terminal 2: Start Backend
.venv/bin/python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000

# Open browser: http://localhost:4200
```

### Option 2: Electron + Browser (Container + Host)

For testing Electron integration:

```bash
# Terminal 1 (Container): Full Stack
python scripts/environment.py fullstack

# Terminal 2 (Host - macOS/Windows/Linux):
cd electron
npm install  # first time only
npm run dev

# Both browser (http://localhost:4200) and Electron work simultaneously!
```

## First Time Setup

### In Dev Container

```bash
# Already done automatically by devcontainer.json
# If needed manually:
cd frontend
npm install
```

### On macOS Host (for Electron)

```bash
# Navigate to project root on macOS
cd /path/to/mag-bridge

# Install Electron dependencies
cd electron
npm install
```

### On Windows Host (for Electron)

```bash
# Navigate to project root on Windows
cd C:\path\to\mag-bridge

# Install Electron dependencies
cd electron
npm install
```

### On Linux Host (for Electron)

```bash
# Navigate to project root on Linux
cd /path/to/mag-bridge

# Install Electron dependencies
cd electron
npm install
```

## Production Build

```bash
# On macOS/Windows/Linux host
cd /path/to/mag-bridge
python scripts/environment.py build

# Output:
# frontend/build/app/mac-arm64/MagBridge.app      (macOS)
# frontend/build/app/linux-unpacked/MagBridge     (Linux)
# frontend/build/app/win-unpacked/MagBridge.exe   (Windows)
```

## Key Files Changed

### New Structure
- `electron/` - Electron main process (macOS host only)
  - `package.json` - Electron dependencies
  - `main.js` - Main process
  - `preload.js` - Security bridge
  - `logging.js` - Logging system
  - `app-config.js` - Configuration

### Updated Files
- `frontend/package.json` - Angular only (no Electron deps)
- `scripts/environment.py` - CLI replacing Makefile tasks
- `frontend/src/` - No changes (already uses `window.electronAPI`)

## Benefits

✅ **Dev Container stays clean** - No Electron/graphics deps in Linux
✅ **Parallel development** - Browser and Electron simultaneously
✅ **Faster builds** - No unnecessary dependencies
✅ **Better security** - Electron isolated from dev environment
✅ **macOS native** - Electron runs natively on host

## Troubleshooting

### Electron won't start on macOS

```bash
# Make sure Node.js is installed on macOS (not just in container)
node --version  # Should be 22+

# Reinstall Electron deps
cd electron
rm -rf node_modules package-lock.json
npm install
```

### Electron won't start on Windows

```bash
# Make sure Node.js is installed on Windows
node --version  # Should be 22+

# Reinstall Electron deps
cd electron
rmdir /s node_modules
del package-lock.json
npm install
```

### Port 4200 not accessible from host (Windows)

```bash
# Windows may need host.docker.internal
# Electron automatically detects Windows and uses correct URL

# Verify Docker Desktop is running
# Check: Docker Desktop → Settings → Resources → WSL Integration
```

### Backend connection refused

```bash
# Check backend is running
curl http://localhost:8000/health  # or appropriate endpoint

# Check backend binds to 0.0.0.0 (not 127.0.0.1)
# In uvicorn command: --host 0.0.0.0
```

## Migration Notes

If you were using the old integrated structure:

1. ✅ Old `frontend/main.js` → `electron/main.js`
2. ✅ Old `frontend/package.json` → split into `frontend/` and `electron/`
3. ✅ Angular code → unchanged (already secure)
4. ✅ Dev workflow → improved (can use browser OR Electron)

## Related Documentation

- [environment.py](scripts/environment.py) - CLI for dev servers, build and packaging
- [Electron README](electron/README.md) - Detailed Electron setup
- [Dev Container Setup](.devcontainer/README.md) - Container architecture
