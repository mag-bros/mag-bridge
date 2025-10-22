const { app, BrowserWindow } = require('electron');
const path = require('path');

const isDev = process.env.NODE_ENV === 'development';

if (isDev) {
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
      nodeIntegration: true,
    },
  });

  if (isDev) {
    win.loadURL('http://localhost:4200'); // Angular dev server
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, 'dist/mag-bridge/browser/index.html'));
  }
}

app.whenReady().then(createWindow);

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
