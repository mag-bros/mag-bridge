const path = require('path');

function getAppConfig() {
  return {
    manageBackend: process.env.BACKEND_EXTERNAL !== '1',

    python: process.env.BACKEND_CMD || (process.platform === 'win32' ? 'python' : 'python3'),

    cwd: process.env.BACKEND_CWD || path.join(__dirname, '..'),

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
  };
}

module.exports = { getAppConfig };
