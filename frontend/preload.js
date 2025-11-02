// frontend/preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Safe API bridge
contextBridge.exposeInMainWorld('electronAPI', {
  apiRequest: (url, method, body) => ipcRenderer.invoke('api-request', { url, method, body }),
});

// Serialize console args robustly and strip %c CSS style args
function serializeArg(a) {
  if (a instanceof Error) {
    return JSON.stringify({ name: a.name, message: a.message, stack: a.stack });
  }
  if (typeof a === 'object') {
    try {
      return JSON.stringify(a);
    } catch {
      try {
        return String(a);
      } catch {
        return '[unserializable-object]';
      }
    }
  }
  return String(a);
}

function stripPercentCAndStyles(args) {
  if (!args.length) return args;
  const parts = [];
  let i = 0;
  while (i < args.length) {
    const s = String(args[i]);
    if (s.includes('%c')) {
      const cnt = (s.match(/%c/g) || []).length;
      parts.push(s.replace(/%c/g, ''));
      i += 1 + cnt; // skip CSS args following each %c
    } else {
      parts.push(s);
      i += 1;
    }
  }
  return parts;
}

// Forward browser console logs to main
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
    original(...args);
  };
});

// Forward unhandled errors
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
