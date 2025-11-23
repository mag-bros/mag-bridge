// frontend/app-settings.js
const fs = require('fs');
const path = require('path');
const pkg = require('./package.json');

/**
 * PathResolver – helper do rozwiązywania ścieżek w dev/release
 */
const PathResolver = {
  repoRoot() {
    // katalog wyżej niż frontend/
    return path.resolve(__dirname, '..');
  },

  releaseRoot() {
    // priorytet: zmienna środowiskowa → katalog zasobów aplikacji → repoRoot
    if (process.env.MAGBRIDGE_DATA_DIR) {
      return process.env.MAGBRIDGE_DATA_DIR;
    }
    if (process.resourcesPath) {
      return path.join(process.resourcesPath, 'magbridge');
    }
    return PathResolver.repoRoot();
  },

  baseDir(isRelease) {
    return isRelease ? PathResolver.releaseRoot() : PathResolver.repoRoot();
  },

  /**
   * Zwraca pełną ścieżkę do katalogu SDF:
   * - central.sdf_dir może być absolutne → używane 1:1
   * - albo względne → liczone względem baseDir (dev/release)
   * - fallback, jeśli brak: 'sdf' pod baseDir
   */
  userSdfDir(isRelease, central) {
    const rawSdfDir = (central && central.sdf_dir) || 'sdf';
    const baseDir = PathResolver.baseDir(isRelease);

    if (path.isAbsolute(rawSdfDir)) {
      return rawSdfDir;
    }
    return path.resolve(baseDir, rawSdfDir);
  },
};

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

function getAppSettings() {
  const isRelease = (process.env.NODE_ENV || pkg.env?.NODE_ENV) === 'release';
  const central = loadCentralConfig(isRelease);

  return {
    isRelease: isRelease,
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
    userSdfDir: PathResolver.userSdfDir(isRelease, central),
    themes: central.themes || {},
  };
}

function configToString(cfg) {
  try {
    return JSON.stringify(cfg, null, 2);
  } catch (_) {
    return '[unserializable-config]';
  }
}

module.exports = { getAppSettings, configToString, PathResolver };
