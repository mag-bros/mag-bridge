// frontend/main.js
const { spawn } = require('child_process');
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const pkg = require('./package.json');
const { createLogger } = require('./logging');
const { getAppConfig } = require('./app-config');

cfg = getAppConfig();

const isRelease = (process.env.NODE_ENV || pkg.env?.NODE_ENV) === 'release';

const log = createLogger({
  isRelease,
  writeToFile: true, // also write in dev
  consoleColors: true,
  cloneConsole: true,
  captureConsole: false,
});

console.log('Log file:', (log.paths && (log.paths.file || log.paths.json)) || '(unknown)');
console.log(`🔧 NODE_ENV = ${process.env.NODE_ENV || '(undefined)'}`);
console.log(`🔧 PKG_ENV = ${pkg.env?.NODE_ENV || '(undefined)'}`);
console.log(`📦 isRelease = ${isRelease}`);

let backendProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 1000,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  log.bindWindow(win, 'main');

  if (!isRelease) {
    win.loadURL('http://localhost:4200');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, 'build/frontend/browser/index.html'));
  }
}

app.whenReady().then(() => {
  try {
    if (cfg.manageBackend) {
      if (isRelease) {
        // Packaged backend binary
        const backendPath = path.join(
          process.resourcesPath,
          'backend',
          process.platform === 'win32' ? 'backend_app.exe' : 'backend_app',
        );
        log.info('spawning backend (release)', { path: backendPath });
        backendProcess = spawn(backendPath, {
          stdio: ['ignore', 'pipe', 'pipe'],
          env: { ...process.env, PYTHONUNBUFFERED: '1' },
        });
        log.hookChildProcess(backendProcess, { name: 'backend' });
      } else {
        // DEV: uvicorn with forced colors (since stdio is piped, no TTY)
        const args = [];
        if (cfg.importTime) args.push('-X', 'importtime');
        args.push(
          '-m',
          'uvicorn',
          cfg.uvicorn.app,
          '--host',
          cfg.uvicorn.host,
          '--port',
          String(cfg.uvicorn.port),
          '--log-level',
          cfg.uvicorn.logLevel,
          '--use-colors', // <<< force ANSI color in uvicorn output
        );
        if (!cfg.uvicorn.accessLog) args.push('--no-access-log');
        if (cfg.uvicorn.useUvloop) args.push('--loop', 'uvloop');
        if (cfg.uvicorn.useHttptools) args.push('--http', 'httptools');
        if (cfg.uvicorn.lifespanOff) args.push('--lifespan', 'off');
        if (cfg.uvicorn.reload) args.push('--reload');

        const env = {
          ...process.env,
          PYTHONUNBUFFERED: '1',
          PYTHONPATH: [cfg.cwd, process.env.PYTHONPATH || ''].filter(Boolean).join(path.delimiter),
          FORCE_COLOR: '1', // <<< hint for color-aware libs
        };

        log.info('spawning backend (dev)', { cmd: cfg.python, args: args.join(' '), cwd: cfg.cwd });
        backendProcess = spawn(cfg.python, args, {
          cwd: cfg.cwd,
          stdio: ['ignore', 'pipe', 'pipe'],
          env,
        });
        log.hookChildProcess(backendProcess, { name: 'backend' });
      }
    } else {
      log.warn('BACKEND_EXTERNAL=1 — not spawning backend (assuming managed externally)');
    }
  } catch (err) {
    log.error(`backend spawn error: ${err?.message || err}`, { src: 'backend' });
  }

  // consume renderer logs
  log.registerFrontendIpc(ipcMain, 'frontend-log');

  setTimeout(createWindow, 100);
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  if (backendProcess) backendProcess.kill();
  log.info('app quitting');
});

// IPC example
ipcMain.handle('api-request', async (_event, { url, method = 'GET', body = null }) => {
  try {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) options.body = JSON.stringify(body);
    const response = await fetch(url, options);
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    return await response.json();
  } catch (err) {
    log.error(`api-request error: ${err.message}`, { url, method });
    throw err;
  }
});
