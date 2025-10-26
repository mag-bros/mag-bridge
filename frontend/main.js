const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

const isRelease = process.env.NODE_ENV === 'release';
let backendProcess;

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
    win.loadFile(path.join(__dirname, '../build/frontend/browser/index.html'));
  }
}

app.whenReady().then(() => {
  if (isRelease) {
    const backendPath = path.join(process.resourcesPath, 'backend', 'backend_app');
    backendProcess = spawn(backendPath, { stdio: 'inherit' });
  }

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
});
