// frontend/logging.js
// Minimal logger: colored console + single file in ~/.magbridge/logs, no rotation.
// Format example:
// ts=2025-10-26T22:08:05.907Z {level='info', msg='Application startup complete.', pid=44341, ver='electron/38.4.0', window='main:1', src='backend', stream='stdout'}

const fs = require('fs');
const path = require('path');
const os = require('os');

// ANSI utilities
const ANSI_RE = /\x1B\[[0-9;]*[A-Za-z]/g;
const stripAnsi = (s) => String(s).replace(ANSI_RE, '');
const COLORS = {
  reset: '\x1b[0m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  lightblue: '\x1b[94m',
  gray: '\x1b[90m',
};

function colorFor(level) {
  switch (level) {
    case 'error':
      return COLORS.red;
    case 'warn':
      return COLORS.yellow;
    case 'debug':
      return COLORS.blue;
    case 'info':
    default:
      return COLORS.lightblue;
  }
}

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

// Normalize backend (uvicorn/gunicorn) style lines, stripping redundant prefixes
function normalizeBackendLine(raw) {
  let line = String(raw).replace(/\r/g, '').trim();
  if (!line) return null;

  // Extract possible level keyword
  const m = line.match(/^\s*(INFO|ERROR|WARNING|WARN|DEBUG)\s*:?\s*/i);
  let lvl = null;
  if (m) {
    const tag = m[1].toUpperCase();
    if (tag === 'WARN' || tag === 'WARNING') lvl = 'warn';
    else lvl = tag.toLowerCase();
    line = line.slice(m[0].length);
  }
  return { line, lvl };
}

// Quote value for file line (no JSON escaping)
function quoteValue(v) {
  if (v === null || v === undefined) return 'null';
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  let s = String(v)
    .replace(/[\r\n\t]+/g, ' ')
    .trim()
    .replace(/'/g, '’'); // typographic apostrophe
  return `'${s}'`;
}

// Build log line: ts=... {level=..., msg='...', ...}
function formatLine(rec) {
  const order = ['level', 'msg', 'pid', 'ver', 'window', 'src', 'stream'];
  const seen = new Set(['ts']);
  const parts = [];

  for (const k of order) {
    if (rec[k] !== undefined) {
      parts.push(`${k}=${quoteValue(rec[k])}`);
      seen.add(k);
    }
  }
  for (const [k, v] of Object.entries(rec)) {
    if (!seen.has(k)) parts.push(`${k}=${quoteValue(v)}`);
  }
  return `ts=${quoteValue(rec.ts)} {${parts.join(', ')}}\n`;
}

function createLogger({
  appName = 'magbridge',
  baseDir = path.join(os.homedir(), '.magbridge', 'logs'),
  fileName = 'magbridge.log',
  writeToFile = true,
  consoleColors = true,
  cloneConsole = true,
  captureConsole = false,
  isRelease = false,
} = {}) {
  ensureDir(baseDir);
  const filePath = path.join(baseDir, fileName);

  const originalConsole = {
    log: console.log.bind(console),
    info: console.info.bind(console),
    warn: console.warn.bind(console),
    error: console.error.bind(console),
    debug: console.debug.bind(console),
  };

  const context = {
    pid: process.pid,
    ver: process.versions?.electron
      ? `electron/${process.versions.electron}`
      : `node/${process.version}`,
  };

  function emit(level, msg, extra) {
    const ts = new Date().toISOString();
    const record = {
      ts,
      level,
      msg: String(msg),
      ...context,
      ...(extra && typeof extra === 'object' ? extra : null),
    };

    // File (strip ANSI)
    if (writeToFile) {
      try {
        fs.appendFileSync(filePath, formatLine({ ...record, msg: stripAnsi(record.msg) }));
      } catch (_) {}
    }

    // Console (with colors)
    if (cloneConsole) {
      const writer = originalConsole[level] || originalConsole.log;
      if (consoleColors) {
        const c = colorFor(level);
        writer(
          `${COLORS.dim}[${ts}]${COLORS.reset} ${c}${level.toUpperCase()}${COLORS.reset}: ${record.msg}`,
        );
      } else {
        writer(`[${ts}] ${level.toUpperCase()}: ${record.msg}`);
      }
    }
  }

  const api = {
    info: (m, e) => emit('info', m, e),
    warn: (m, e) => emit('warn', m, e),
    error: (m, e) => emit('error', m, e),
    debug: (m, e) => emit('debug', m, e),

    captureConsole() {
      console.log = (...a) => api.info(a.join(' '));
      console.info = (...a) => api.info(a.join(' '));
      console.warn = (...a) => api.warn(a.join(' '));
      console.error = (...a) => api.error(a.join(' '));
      console.debug = (...a) => api.debug(a.join(' '));
    },

    bindWindow(win, label = 'main') {
      try {
        context.window = `${label}:${win?.id ?? 'unknown'}`;
      } catch (_) {}
    },

    registerFrontendIpc(ipcMain, channel = 'frontend-log') {
      ipcMain.on(channel, (_evt, payload) => {
        const { level = 'info', message = '' } = payload || {};
        const safe = String(message);
        switch (level) {
          case 'error':
            return api.error(safe, { src: 'frontend' });
          case 'warn':
            return api.warn(safe, { src: 'frontend' });
          case 'debug':
            return api.debug(safe, { src: 'frontend' });
          default:
            return api.info(safe, { src: 'frontend' });
        }
      });
    },

    hookChildProcess(child, { name = 'child' } = {}) {
      if (!child) return;

      const handleChunk = (chunk, stream) => {
        String(chunk)
          .split(/\n/)
          .forEach((raw) => {
            const norm = normalizeBackendLine(raw);
            if (!norm) return;
            let { line, lvl } = norm;

            // Strip redundant prefixes entirely (INFO:, ERROR:, etc.)
            line = line.replace(/^\s*(INFO|ERROR|WARNING|WARN|DEBUG)\s*:?\s*/i, '');

            let level;
            if (lvl) level = lvl;
            else if (stream === 'stderr') level = 'error';
            else level = 'info';

            if (level === 'error') api.error(line, { src: name, stream });
            else if (level === 'warn') api.warn(line, { src: name, stream });
            else if (level === 'debug') api.debug(line, { src: name, stream });
            else api.info(line, { src: name, stream });
          });
      };

      if (child.stdout) child.stdout.on('data', (d) => handleChunk(d, 'stdout'));
      if (child.stderr) child.stderr.on('data', (d) => handleChunk(d, 'stderr'));
      child.on('exit', (code, sig) =>
        api.info('process exited', { src: name, event: 'exit', code, sig }),
      );
      child.on('error', (err) =>
        api.error(`process error: ${err?.message || err}`, { src: name, event: 'error' }),
      );
    },

    paths: { file: filePath, dir: baseDir },
  };

  if (captureConsole) api.captureConsole();

  api.info('--- logger initialized ---', {
    file: filePath,
    mode: isRelease ? 'release' : 'dev',
  });

  return api;
}

module.exports = { createLogger };
