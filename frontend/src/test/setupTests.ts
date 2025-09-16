import '@testing-library/jest-dom';
// Node polyfills for web encoders used by MSW internals MUST load before MSW
import { TextEncoder, TextDecoder } from 'util';
// @ts-ignore
globalThis.TextEncoder = TextEncoder;
// @ts-ignore
globalThis.TextDecoder = TextDecoder as unknown as typeof globalThis.TextDecoder;
import 'whatwg-fetch';
import { server } from './msw/server';
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
  VITE_API_URL: 'http://localhost:8000/api',
};

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
