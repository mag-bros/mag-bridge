const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  apiRequest: (url, method, body) => ipcRenderer.invoke('api-request', { url, method, body }),
});
