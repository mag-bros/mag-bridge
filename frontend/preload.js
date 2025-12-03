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

// Remove %c formatting (CSS in browser console)
function stripPercentCAndStyles(args) {
  if (!args.length) return args;
  const out = [];
  let i = 0;

  while (i < args.length) {
    const text = String(args[i]);

    if (text.includes('%c')) {
      const cnt = (text.match(/%c/g) || []).length;
      out.push(text.replace(/%c/g, ''));
      i += 1 + cnt;
    } else {
      out.push(text);
      i++;
    }
  }

  return out;
}

// Patch console.* and forward messages to main
['log', 'warn', 'error', 'info', 'debug'].forEach((level) => {
  const original = console[level];

  console[level] = (...args) => {
    try {
      const stripped = stripPercentCAndStyles(args);
      const msg = stripped.map(serializeArg).join(' ');
      ipcRenderer.send('frontend-log', { level, message: msg });
    } catch {
      ipcRenderer.send('frontend-log', { level: 'error', message: '[log serialization failed]' });
    }

    // Still print to local renderer DevTools
    original(...args);
  };
});

// ============================================================================
// 4. Unhandled Error Forwarding
// ============================================================================

window.addEventListener('error', (event) => {
  ipcRenderer.send('frontend-log', {
    level: 'error',
    message: `Unhandled error: ${event.message}`,
  });
});

window.addEventListener('unhandledrejection', (event) => {
  ipcRenderer.send('frontend-log', {
    level: 'error',
    message: `Unhandled rejection: ${serializeArg(event.reason)}`,
  });
});
