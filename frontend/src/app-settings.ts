// src/app-settings.ts

export interface MagBridgeConfig {
  sdf_dir: string;
  themes: Record<string, unknown>;
}

interface PreloadSettings {
  isRelease: boolean;
  config: MagBridgeConfig;
}

const rawSettings: PreloadSettings = (() => {
  const s = (window as any).magBridgeSettings as PreloadSettings | undefined;
  if (!s) {
    throw new Error('magBridgeSettings missing. Preload did not expose settings.');
  }
  return s;
})();

export class AppSettings {
  static readonly isRelease: boolean = rawSettings.isRelease;
  static readonly config: MagBridgeConfig = rawSettings.config;
}
