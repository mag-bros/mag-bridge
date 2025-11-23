const os = require('os');
const path = require('path');
const pkg = require('./package.json');

const PathResolver = {
  baseDir(isRelease) {
    return path.join(os.homedir(), isRelease ? 'magbridge' : 'magbridge-dev');
  },

  userSdfDir(isRelease) {
    return path.join(this.baseDir(isRelease), 'userdata', 'sdf');
  },

  logFile(isRelease) {
    return path.join(this.baseDir(isRelease), 'app.log');
  },
};

function getAppConfig() {
  const isRelease = (process.env.NODE_ENV || pkg.env?.NODE_ENV) === 'release';

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

    userSdfDir: PathResolver.userSdfDir(isRelease),
    logFile: PathResolver.logFile(isRelease),
  };
}

function configToString(cfg) {
  try {
    return JSON.stringify(cfg, null, 2);
  } catch (_) {
    return '[unserializable-config]';
  }
}

module.exports = { getAppConfig, configToString, PathResolver };
