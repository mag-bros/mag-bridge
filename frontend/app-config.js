const os = require('os');
const path = require('path');
const pkg = require('./package.json');

function getAppConfig() {
  const isProd = (process.env.NODE_ENV || pkg.env?.NODE_ENV) === 'production';

  return {
    // environment
    isProd: isProd,
    nodeEnv: process.env.NODE_ENV || pkg.env?.NODE_ENV || 'production',
    runMode: process.env.RUN_MODE || pkg.env?.RUN_MODE || 'default',
    pkgEnv: pkg.env?.NODE_ENV || '(undefined)',

    // paths
    backendExecutablePath: PathResolver.getBackendExecutablePath(isProd) || '(undefined)',
    userSdfDir: PathResolver.userSdfDir(isProd),
    logFile: PathResolver.logFile(isProd),

    // core backend control
    manageBackend: process.env.MANAGE_BACKEND == '1' || true,
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

    // utils
    importTime: process.env.BACKEND_IMPORTTIME === '1',
  };
}

const PathResolver = {
  baseDir(isProd) {
    // Linux/mac example: /home/user/magbridge
    return path.join(os.homedir(), isProd ? 'magbridge' : 'magbridge-dev');
  },

  userSdfDir(isProd) {
    // Linux/mac example: /home/user/magbridge/userdata/sdf
    return path.join(this.baseDir(isProd), 'userdata', 'sdf');
  },

  logFile(isProd) {
    // Linux/mac example: /home/user/magbridge/app.log
    return path.join(this.baseDir(isProd), 'app.log');
  },

  getBackendExecutablePath(isProd) {
    if (isProd) {
      return path.join(
        process.resourcesPath,
        'backend',
        'backend_app',
        process.platform === 'win32' ? 'backend_app.exe' : 'backend_app'
      );
    }

    return 'N/A - backend managed by developer';
  }
};

function configToString(cfg) {
  try {
    return JSON.stringify(cfg, null, 2);
  } catch (_) {
    return '[unserializable-config]';
  }
}

module.exports = { getAppConfig, configToString, PathResolver };
