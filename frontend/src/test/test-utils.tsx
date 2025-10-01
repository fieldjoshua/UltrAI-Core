import React from 'react';
// Ensure Vite-like env defaults exist during tests
// @ts-ignore
globalThis.import = globalThis.import || {};
// @ts-ignore
globalThis.import.meta = globalThis.import.meta || { env: {} };
// @ts-ignore
globalThis.import.meta.env = {
  ...(globalThis.import.meta.env || {}),
  VITE_API_MODE: globalThis.import.meta.env?.VITE_API_MODE || 'test',
  VITE_DEMO_MODE: globalThis.import.meta.env?.VITE_DEMO_MODE || 'false',
};
import { render, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Create a custom render function that includes all providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialRoutes?: string[];
}

export function renderWithProviders(
  ui: React.ReactElement,
  { initialRoutes = ['/'], ...renderOptions }: CustomRenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <MemoryRouter initialEntries={initialRoutes}>{children}</MemoryRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

// Re-export everything from testing library
export * from '@testing-library/react';
export { renderWithProviders as render };

// Mock data generators
export const mockUser = (overrides = {}) => ({
  id: '123',
  email: 'test@example.com',
  name: 'Test User',
  ...overrides,
});

export const mockModel = (overrides = {}) => ({
  name: 'gpt-4',
  provider: 'openai',
  cost_per_1k_tokens: 0.03,
  is_available: true,
  ...overrides,
});

export const mockOrchestratorResult = (overrides = {}) => ({
  status: 'success',
  ultra_response: 'Test synthesis response',
  models_used: ['gpt-4', 'claude-3', 'gemini-1.5-pro'],
  processing_time: 4.73,
  pattern_used: 'comparative',
  initial_responses: [],
  meta_analysis: { content: 'Meta analysis content' },
  ...overrides,
});

// Common test helpers
export const waitForLoadingToFinish = () =>
  screen.findByText((content, element) => {
    return element?.tagName.toLowerCase() !== 'script';
  });

// Orchestrator test helpers
// Provide global helpers that individual tests can call without importing
// These wire into the jest-mocked orchestrator API when available
try {
  // Lazy import to avoid issues in non-test runtimes
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const orchestratorApi = require('../api/orchestrator');

  const setNextOrchestrationResult = (result: unknown) => {
    const fn: any = orchestratorApi?.processWithFeatherOrchestration;
    if (fn && typeof fn.mockImplementationOnce === 'function') {
      fn.mockImplementationOnce(async () => result);
    } else if (typeof fn === 'function') {
      orchestratorApi.processWithFeatherOrchestration = async () => result;
    }
  };

  const setNextOrchestrationError = (error: unknown) => {
    const fn: any = orchestratorApi?.processWithFeatherOrchestration;
    if (fn && typeof fn.mockImplementationOnce === 'function') {
      fn.mockImplementationOnce(async () => {
        throw error;
      });
    } else if (typeof fn === 'function') {
      orchestratorApi.processWithFeatherOrchestration = async () => {
        throw error;
      };
    }
  };

  const setAvailableModels = (models: string[]) => {
    const fn: any = orchestratorApi?.getAvailableModels;
    const value = { models } as any;
    if (fn && typeof fn.mockResolvedValueOnce === 'function') {
      fn.mockResolvedValueOnce(value);
    } else if (typeof fn === 'function') {
      orchestratorApi.getAvailableModels = async () => value;
    }
  };

  (globalThis as any).__setOrchestrationNextResult = setNextOrchestrationResult;
  (globalThis as any).__setOrchestrationNextError = setNextOrchestrationError;
  (globalThis as any).__setAvailableModels = setAvailableModels;
} catch {
  // Ignore if orchestrator API cannot be required in this context
}
