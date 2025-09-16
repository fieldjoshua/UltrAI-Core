// Pre-module setup for Jest: define Vite-like import.meta.env and required polyfills
import { TextEncoder, TextDecoder } from 'util';
// @ts-ignore
(globalThis as any).TextEncoder = TextEncoder;
// @ts-ignore
(globalThis as any).TextDecoder = TextDecoder as unknown as typeof globalThis.TextDecoder;
// Polyfill Web Streams used by MSW interceptors (global polyfill)
import 'web-streams-polyfill/polyfill';
// Minimal BroadcastChannel polyfill for Node test environment
if (typeof (globalThis as any).BroadcastChannel === 'undefined') {
  class NodeBroadcastChannel {
    name: string;
    onmessage: ((this: NodeBroadcastChannel, ev: MessageEvent) => any) | null = null;
    private static channels: Record<string, Set<NodeBroadcastChannel>> = {};

    constructor(name: string) {
      this.name = name;
      if (!NodeBroadcastChannel.channels[name]) {
        NodeBroadcastChannel.channels[name] = new Set();
      }
      NodeBroadcastChannel.channels[name].add(this);
    }

    postMessage(message: any) {
      for (const client of NodeBroadcastChannel.channels[this.name]) {
        if (client !== this && typeof client.onmessage === 'function') {
          client.onmessage({ data: message } as MessageEvent);
        }
      }
    }

    close() {
      NodeBroadcastChannel.channels[this.name].delete(this);
    }

    addEventListener(_type: string, listener: any) {
      this.onmessage = listener;
    }

    removeEventListener(_type: string, _listener: any) {
      this.onmessage = null;
    }
  }
  // @ts-ignore
  (globalThis as any).BroadcastChannel = NodeBroadcastChannel as any;
}
import 'whatwg-fetch';
// @ts-ignore
(globalThis as any).import = (globalThis as any).import || {};
// @ts-ignore
(globalThis as any).import.meta = (globalThis as any).import.meta || {
  env: {},
};
// @ts-ignore
(globalThis as any).import.meta.env = {
  ...(globalThis as any).import.meta.env,
  VITE_APP_MODE: 'test',
  VITE_API_MODE: 'test',
  VITE_DEFAULT_SKIN: 'night',
  VITE_API_URL: 'http://localhost:8000/api',
};
