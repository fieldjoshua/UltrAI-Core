import '@testing-library/jest-dom';
// Provide minimal import.meta.env for modules that reference Vite env vars
// @ts-ignore
globalThis.import = { meta: { env: { VITE_API_URL: 'http://localhost:8000/api' } } } as any;
// Also provide import.meta for direct access
// @ts-ignore
globalThis.import = globalThis.import || {};
// @ts-ignore
globalThis.import.meta = globalThis.import.meta || { env: { VITE_API_URL: 'http://localhost:8000/api' } };


