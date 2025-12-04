export interface AppConfigShape {
  isRelease: boolean;
  config: {
    sdf_dir: string;
    themes: Record<string, unknown>;
  };
  [key: string]: unknown;
}

declare global {
  interface Window {
    appConfig?: AppConfigShape;
  }
}

const rawConfig: AppConfigShape = (() => {
  const c = window.appConfig;
  if (!c) {
    throw new Error('appConfig missing. Preload did not expose appConfig.');
  }
  return c;
})();

export class AppConfig {
  static readonly isRelease = rawConfig.isRelease;
  static readonly config = rawConfig.config;
  static readonly userSdfDir = rawConfig.config.sdf_dir;
}
