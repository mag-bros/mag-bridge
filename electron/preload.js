// ============================================================================
// FRONTEND PRELOAD (Electron Renderer Bridge)
// Provides:
//   - apiRequest IPC bridge
//   - stdout logger (explicit logging to main)
//   - console forwarding (renderer console -> main)
//   - unhandled error forwarding
// ============================================================================

const { contextBridge, ipcRenderer } = require('electron');

// ============================================================================
// 1. IPC Wrapper: Safe API Request
// ============================================================================

// Safe API bridge
contextBridge.exposeInMainWorld('electronAPI', {
  apiRequest: (url, method, body) => ipcRenderer.invoke('api-request', { url, method, body }),
  selectFile: () => ipcRenderer.invoke('select-file'),
});

// ============================================================================
// 2. Explicit Renderer → Main Logging (stdout bridge)
// ============================================================================

contextBridge.exposeInMainWorld('stdout', {
  log: (...args) => ipcRenderer.send('frontend-log', { level: 'info', args }),
  warn: (...args) => ipcRenderer.send('frontend-log', { level: 'warn', args }),
  error: (...args) => ipcRenderer.send('frontend-log', { level: 'error', args }),
  debug: (...args) => ipcRenderer.send('frontend-log', { level: 'debug', args }),
});

// ============================================================================
// 3. Internal Renderer Console Forwarding (optional)
// Sends all console.log/info/warn/error/debug to main log
// ============================================================================

// Serialize console args robustly (objects, errors, primitives)
function serializeArg(a) {
  if (a instanceof Error) {
    return JSON.stringify({ name: a.name, message: a.message, stack: a.stack });
  }
  if (typeof a === 'object') {
    try {
      return JSON.stringify(a);
    } catch {
      return String(a);
    }
  }
  return String(a);
}

['log', 'info', 'warn', 'error', 'debug'].forEach((level) => {
  const original = console[level];

  console[level] = function (...args) {
    try {
      const serialized = args.map(serializeArg);
      ipcRenderer.send('frontend-log', {
        level: level === 'log' ? 'info' : level,
        args: serialized,
      });
    } catch (_) {
      // ignore
    }

    original.apply(console, args);
  };
});

// ============================================================================
// 4. Unhandled Error Forwarding
// ============================================================================

window.addEventListener('error', (evt) => {
  const msg = `[Unhandled Error] ${evt.message} at ${evt.filename}:${evt.lineno}:${evt.colno}`;
  try {
    ipcRenderer.send('frontend-log', { level: 'error', args: [msg] });
  } catch (e) {
    console.error('[preload IPC failed]', msg, e);
  }
});

window.addEventListener('unhandledrejection', (evt) => {
  const msg = `[Unhandled Promise Rejection] ${String(evt.reason)}`;
  try {
    ipcRenderer.send('frontend-log', { level: 'error', args: [msg] });
  } catch (e) {
    console.error('[preload IPC failed]', msg, e);
  }
});
