export {};

declare global {
  interface Window {
    electronAPI: {
      apiRequest: (url: string, method: string, body?: any) => Promise<any>;
      selectFile: () => Promise<string | null>;
    };
  }
}
