import '@testing-library/jest-dom';
// Provide minimal import.meta.env for modules that reference Vite env vars
// @ts-ignore
globalThis.import = globalThis.import || {};
// @ts-ignore
globalThis.import.meta = globalThis.import.meta || { env: {} };
// @ts-ignore
globalThis.import.meta.env = {
  ...(globalThis.import.meta.env || {}),
  VITE_APP_MODE: 'test',
  VITE_API_MODE: 'test',
  VITE_DEFAULT_SKIN: 'night',
  VITE_API_URL: 'http://localhost:8000/api'
};


