// Pre-module setup for Jest: define Vite-like import.meta.env
// @ts-ignore
(globalThis as any).import = (globalThis as any).import || {};
// @ts-ignore
(globalThis as any).import.meta = (globalThis as any).import.meta || { env: {} };
// @ts-ignore
(globalThis as any).import.meta.env = {
  ...(globalThis as any).import.meta.env,
  VITE_APP_MODE: 'test',
  VITE_API_MODE: 'test',
  VITE_DEFAULT_SKIN: 'night',
  VITE_API_URL: 'http://localhost:8000/api',
};
