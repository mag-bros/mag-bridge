// frontend/app-config.js
const fs = require('fs');
const path = require('path');
const pkg = require('./package.json');

function loadCentralConfig(isRelease) {
  try {
    // tryb release: plik siedzi wewnątrz asara → build/frontend/browser/magbridge-config.json
    const releasePath = path.join(
      __dirname,
      'build',
      'frontend',
      'browser',
      'magbridge-config.json',
    );

    const devPath = path.join(__dirname, '..', 'magbridge-config.json');

    const cfgPath = isRelease ? releasePath : devPath;

    const raw = fs.readFileSync(cfgPath, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    console.error(`Failed to load magbridge-config.json: ${err.message}`);
    return {};
  }
}

function getAppConfig() {
  const isRelease = (process.env.NODE_ENV || pkg.env?.NODE_ENV) === 'release';

  // wczytanie centralnego pliku konfiguracyjnego użytkownika
  const central = loadCentralConfig(isRelease);

  return {
    isRelease,
    nodeEnv: process.env.NODE_ENV || '(undefined)',
    pkgEnv: pkg.env?.NODE_ENV || '(undefined)',

    // core backend control
    manageBackend: process.env.BACKEND_EXTERNAL !== '1',
    python: process.env.BACKEND_CMD || (process.platform === 'win32' ? 'python' : 'python3'),
    cwd: process.env.BACKEND_CWD || path.join(__dirname, '..'),

    // uvicorn config
    uvicorn: {
      app: process.env.UVICORN_APP || 'backend:app',
      host: process.env.UVICORN_HOST || '127.0.0.1',
      port: Number(process.env.UVICORN_PORT || 8000),
      logLevel: process.env.UVICORN_LOG_LEVEL || 'info',
      accessLog: (process.env.UVICORN_ACCESS_LOG ?? '1') !== '0',
      reload: process.env.UVICORN_RELOAD === '1',
      useUvloop: process.env.UVICORN_UVLOOP === '1',
      useHttptools: process.env.UVICORN_HTTPTOOLS === '1',
      lifespanOff: process.env.UVICORN_LIFESPAN_OFF === '1',
    },

    importTime: process.env.BACKEND_IMPORTTIME === '1',

    userSdfDir: central.sdf_dir,
    themes: central.themes,
  };
}

function configToString(cfg) {
  try {
    return JSON.stringify(cfg, null, 2);
  } catch (_) {
    return '[unserializable-config]';
  }
}

module.exports = { getAppConfig, configToString };
