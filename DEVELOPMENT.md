# 🛠️ MagBridge - Developer Guide

## Architecture

MagBridge uses a **sidecar architecture** for optimal development experience:

- **Frontend (Angular)** → Runs in Dev Container (Linux)
- **Backend (FastAPI)** → Runs in Dev Container (Linux)  
- **Electron** → Runs on macOS host (outside container)

```
┌──────────────────────────────────┐
│  macOS Host                      │
│  ┌────────────────────────────┐  │
│  │  Electron (electron/)      │  │
│  │  → http://localhost:4200   │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
           ↓ Port forwarding
┌──────────────────────────────────┐
│  Dev Container (Linux)           │
│  ┌────────────────────────────┐  │
│  │  Angular :4200             │  │
│  │  Backend :8000             │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## Quick Start

### For Angular Development (Container)

```bash
# Start Angular dev server
./dev.sh

# Or manually:
cd frontend
npm run serve-reloader

# Open http://localhost:4200 in browser
```

### For Full Stack Development (Container + Backend)

```bash
# Terminal 1: Angular
./dev.sh

# Terminal 2: Backend
.venv/bin/python -m uvicorn backend:app --reload --host 0.0.0.0
```

### For Electron Development (macOS Host)

```bash
# Prerequisites:
# 1. Dev container running with Angular on :4200
# 2. Node.js 22+ installed on macOS

# On macOS host (outside container):
cd electron
npm install  # first time only
./dev.sh     # or: npm run dev
```

## Project Structure

```
mag-bridge/
├── electron/              # Electron (macOS host only)
│   ├── package.json      # Electron dependencies
│   ├── main.js           # Main process
│   ├── preload.js        # Security bridge
│   └── dev.sh            # Dev script (macOS)
│
├── frontend/             # Angular (Dev Container)
│   ├── package.json      # Angular dependencies
│   ├── src/              # Angular source code
│   └── build/            # Build outputs
│
├── backend/              # FastAPI (Dev Container)
│   └── main.py           # Backend entry point
│
├── src/                  # Core Python library
│   └── core/             # RDKit-based core logic
│
├── tests/                # Test suite (500+ tests)
│   └── core/             # Core module tests
│
├── data/                 # SDF files (test data)
│   └── sdf/              # Molecular structure files
│
├── notebooks/            # Jupyter notebooks
│   ├── pubchem-tool.ipynb        # Test case generator
│   └── substruct-matching.ipynb  # Visualization tool
│
├── .devcontainer/        # Dev Container config
│   ├── Dockerfile        # Container image
│   └── devcontainer.json # VSCode config
│
├── Makefile              # Build automation
├── dev.sh                # Quick dev start (container)
├── QUICKSTART.md         # Quick start guide
├── DEVELOPMENT.md        # This file
└── MIGRATION.md          # Electron migration notes
```

## Development Workflows

### Workflow 1: Browser-Only Development

**Best for:** Pure Angular/UI work, no Electron testing needed

```bash
# In container
./dev.sh

# Access in browser: http://localhost:4200
```

**Benefits:**
- ✅ Fast refresh with HMR
- ✅ Chrome DevTools
- ✅ No Electron overhead

### Workflow 2: Electron Testing

**Best for:** Testing Electron integration, native features

```bash
# Terminal 1 (Container): Angular
./dev.sh

# Terminal 2 (Container): Backend
make backend

# Terminal 3 (macOS Host): Electron
cd electron && ./dev.sh
```

**Benefits:**
- ✅ Test native macOS features
- ✅ Test IPC communication
- ✅ Test file system access
- ✅ Both browser and Electron work simultaneously

### Workflow 3: Python/Backend Development

**Best for:** Backend API, core RDKit logic

```bash
# Start backend with auto-reload
.venv/bin/python -m uvicorn backend:app --reload --host 0.0.0.0

# Run tests
pytest tests/core/

# Access API docs: http://localhost:8000/docs
```

## Common Commands

### Makefile Commands

```bash
make build          # Build complete app (Angular + Backend + Electron)
make build-backend  # Build backend executable
make dev            # Start Angular dev server (container)
make backend        # Start backend (container)
make install        # Install frontend dependencies
make clean          # Clean build outputs
make info           # Show build configuration
```

### NPM Commands (Frontend)

```bash
cd frontend
npm run serve-reloader  # Start dev server with HMR
npm run build:prod      # Build production Angular
npm run build:dev       # Build development Angular
npm run test-angular    # Run Angular tests
npm run format-code     # Format code with Prettier
```

### NPM Commands (Electron)

```bash
cd electron
npm run dev             # Start Electron (waits for :4200)
npm run build:mac       # Build macOS app
npm run build:win       # Build Windows app (on Windows)
npm run build:linux     # Build Linux app
```

### Python Commands

```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/core/test_substruct_matching.py

# Run with coverage
pytest --cov=src tests/

# Install Python dependencies
uv pip install -r requirements.txt -r requirements-dev.txt

# Run backend directly
python -m uvicorn backend:app --reload
```

## Testing

### Frontend Tests (Angular)

```bash
cd frontend
npm run test-angular
```

### Backend Tests (Python)

```bash
# All tests
pytest tests/

# Specific module
pytest tests/core/

# With coverage
pytest --cov=src tests/

# Verbose
pytest -v tests/

# Run test drift detection
python tests/scripts/test_drift.py
```

### Test Data

Test cases are in `tests/data/`:
- `substruct_matching_tests.py` - 400+ substructure matching tests
- `diamag_tests.py` - Diamagnetic contribution tests

SDF files in `data/sdf/`:
- `bond_match/` - Bond type matching test data
- `molecule_match/` - Molecule matching test data

## Production Build

### Full Build (macOS)

```bash
# On macOS host (not in container)
cd /path/to/mag-bridge
make build
```

**Output:**
- `frontend/build/frontend/` - Angular build
- `frontend/build/backend/` - Python executable
- `frontend/build/app/mac-arm64/MagBridge.app` - macOS application
- `frontend/build/app/MagBridge-0.0.0-arm64.dmg` - Installer

### Individual Builds

```bash
# Backend only
make build-backend
# Output: frontend/build/backend/backend_app

# Angular only
cd frontend && npm run build:prod
# Output: frontend/build/frontend/

# Electron only (requires Angular + Backend built first)
cd electron && npx electron-builder --mac
# Output: frontend/build/app/
```

## Environment Variables

### Backend Configuration

```bash
# Python executable (default: python3)
BACKEND_CMD=python3.12

# Backend working directory (default: project root)
BACKEND_CWD=/path/to/mag-bridge

# Manage backend process (default: 1)
MANAGE_BACKEND=1

# Uvicorn settings
UVICORN_APP=backend:app
UVICORN_HOST=127.0.0.1
UVICORN_PORT=8000
UVICORN_LOG_LEVEL=info
UVICORN_RELOAD=1
```

### Electron Configuration

```bash
# Environment (development or production)
NODE_ENV=development

# Backend management
MANAGE_BACKEND=1
```

## Logs

### Development Logs

```bash
# Electron logs
tail -f ~/magbridge-dev/app.log

# Backend logs (in terminal where backend runs)
```

### Production Logs

```bash
# Electron + Backend logs
tail -f ~/magbridge/app.log
```

## Troubleshooting

### Container Issues

**Problem:** Dependencies not installed
```bash
# Reinstall dependencies
cd frontend && npm install
uv pip install -r requirements.txt -r requirements-dev.txt
```

**Problem:** Port already in use
```bash
# Check what's using the port
lsof -i :4200
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Electron Issues

**Problem:** Electron won't start on macOS
```bash
# Check Node.js version (need 22+)
node --version

# Reinstall Electron dependencies
cd electron
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Can't connect to Angular
```bash
# Check port forwarding in VSCode
# Ports panel should show 4200 forwarded

# Test connection
curl http://localhost:4200
```

### Backend Issues

**Problem:** Backend won't start
```bash
# Check virtual environment
source .venv/bin/activate
which python

# Check dependencies
pip list | grep rdkit

# Reinstall if needed
uv pip install -r requirements.txt
```

**Problem:** Import errors
```bash
# Set PYTHONPATH
export PYTHONPATH=/workspaces/mag-bridge:$PYTHONPATH

# Or run with -m flag
python -m uvicorn backend:app
```

## Code Quality

### Formatting

```bash
# Format Angular code
cd frontend
npm run format-code

# Format Python code
black src/ tests/ backend/
isort src/ tests/ backend/
```

### Linting

```bash
# Angular linting
cd frontend
ng lint

# Python linting
pylint src/ backend/
mypy src/ backend/
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start for new developers
- [MIGRATION.md](MIGRATION.md) - Electron sidecar migration notes
- [electron/README.md](electron/README.md) - Electron-specific docs
- [.devcontainer/README.md](.devcontainer/README.md) - Dev Container architecture
- [README.md](README.md) - Scientific background and usage

## Contributing

### Before Committing

1. ✅ Run tests: `pytest tests/`
2. ✅ Format code: `black .` and `npm run format-code`
3. ✅ Check errors: No TypeScript/Python errors
4. ✅ Build succeeds: `make build` (on macOS)
5. ✅ Update docs if needed

### Commit Guidelines

- Follow [Conventional Commits](https://www.conventionalcommits.org/)
- Run tests before pushing
- Keep commits atomic and focused
- Write clear commit messages

### Pull Requests

1. Create feature branch: `feat/your-feature`
2. Make changes with tests
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description

## Additional Resources

- [RDKit Documentation](https://www.rdkit.org/docs/)
- [Angular Documentation](https://angular.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Electron Documentation](https://www.electronjs.org/docs)

## Support

For issues or questions:
1. Check existing documentation
2. Search closed issues on GitHub
3. Open new issue with reproduction steps
4. Tag with appropriate labels

---

**Happy Coding! 🚀**
