const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const pkg = require('./package.json');

const isRelease = (process.env.NODE_ENV || pkg.env?.NODE_ENV) === 'release';
console.log(`🔧 NODE_ENV = ${process.env.NODE_ENV || '(undefined)'}`);
console.log(`🔧 PKG_ENV = ${pkg.env?.NODE_ENV || '(undefined)'}`);
console.log(`📦 isRelease = ${isRelease}`);

let backendProcess;
let log = () => {}; // no-op by default

if (isRelease) {
  const logPath = path.join(process.env.HOME || process.env.USERPROFILE, 'magbridge_runtime.log');
  const log = (msg) => {
    const line = `[${new Date().toISOString()}] ${msg}\n`;
    fs.appendFileSync(logPath, line);
    console.log(line);
  };
  global.log = log;
  log('--- App start ---');
}

if (!isRelease) {
  const electronReload = require('electron-reload');
  electronReload(__dirname, {
    electron: path.join(__dirname, 'node_modules', '.bin', 'electron'),
    forceHardReset: true,
    hardResetMethod: 'exit',
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  if (!isRelease) {
    win.loadURL('http://localhost:4200');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, 'build/frontend/browser/index.html'));
  }
}

app.whenReady().then(() => {
  if (isRelease) {
    // start backend
    const backendPath = path.join(process.resourcesPath, 'backend', 'backend_app'); // windows will need .exe
    log(`Spawning backend from: ${backendPath}`);

    try {
      backendProcess = spawn(backendPath, { stdio: ['ignore', 'pipe', 'pipe'] });

      backendProcess.stdout.on('data', (d) => {
        const msg = `[backend] ${d.toString()}`;
        process.stdout.write(msg);
        log(msg);
      });

      backendProcess.stderr.on('data', (d) => {
        const msg = `[backend-err] ${d.toString()}`;
        process.stderr.write(msg);
        log(msg);
      });

      backendProcess.on('exit', (c) => log(`Backend exited with code ${c}`));
      backendProcess.on('error', (err) => log(`[backend-error] ${err.message}`));
    } catch (err) {
      log(`[backend-spawn-error] ${err.message}`);
    }
  }

  setTimeout(createWindow, 100);
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('api-request', async (event, { url, method = 'GET', body = null }) => {
  try {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (err) {
    console.error('Error in api-request handler:', err);
    throw err;
  }
});
