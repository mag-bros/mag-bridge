// frontend/main.js
const { spawn } = require('child_process');
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

const { createLogger } = require('./logging');
const { getAppConfig, configToString } = require('./app-config');
cfg = getAppConfig();
const log = createLogger();

log.info(`=== MagBridge configuration ===\n${configToString(cfg)}`);

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

  if (!cfg.isRelease) {
    win.loadURL('http://localhost:4200');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, 'build/frontend/browser/index.html'));
  }
}

function startProdBackend() {
  log.info('Spawning backend from executable', { path: cfg.backendExecutablePath });

  backendProcess = spawn(cfg.backendExecutablePath, {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
  });

  log.hookChildProcess(backendProcess, { name: 'backend' });
}

function startDevBackend() {
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
    '--use-colors'
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
    FORCE_COLOR: '1',
  };

  log.info('Spawning managed backend (dev)', {
    cmd: cfg.python,
    args: args.join(' '),
    cwd: cfg.cwd,
  });

  backendProcess = spawn(cfg.python, args, {
    cwd: cfg.cwd,
    stdio: ['ignore', 'pipe', 'pipe'],
    env,
  });

  log.hookChildProcess(backendProcess, { name: 'backend' });
}

function onBackendReady() {
  try {
    if (cfg.manageBackend) {
      if (cfg.isRelease) {
        startProdBackend();
      } else {
        startDevBackend();
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
}

app.whenReady().then(onBackendReady);

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

ipcMain.handle('api-request', async (_event, { url, method = 'GET', body = null }) => {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body != null) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const text = await (async () => {
        try {
          return await response.text();
        } catch {
          return '<unreadable body>';
        }
      })();

      const httpError = new Error(`HTTP ${response.status}: ${text}`);
      httpError.status = response.status;
      throw httpError;
    }

    // ✅ success: same behaviour as before – raw JSON goes back to renderer
    return await response.json();

  } catch (err) {
    const info = classifyApiError(err);

    // 🔇 backend not listening yet -> treat as "not ready", don't spam stacktraces
    if (info.kind === 'network' && info.code === 'ECONNREFUSED') {
      // renderer will see `null` and can log a nice "not ready" line
      return null;
    }

    // 🔊 all other errors: log with some structure, then rethrow for renderer
    log.error(`api-request error: ${err?.message || String(err)}`, {
      url,
      method,
      ...info,
    });

    throw err;
  }
});

// helper: classify main error types once, for logging and future use
function classifyApiError(err) {
  const cause = err?.cause || err;
  const code = cause?.code;

  if (code === 'ECONNREFUSED') {
    return { kind: 'network', code: 'ECONNREFUSED' };
  }

  if (code === 'ENOTFOUND') {
    return { kind: 'network', code: 'ENOTFOUND' };
  }

  if (err.status && typeof err.status === 'number') {
    return { kind: 'http', code: `HTTP_${err.status}`, status: err.status };
  }

  return { kind: 'internal', code: cause?.name || 'INTERNAL_ERROR' };
}
