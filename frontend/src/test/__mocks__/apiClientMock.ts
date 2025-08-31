const mockApi = {
  post: jest.fn(),
  get: jest.fn(),
  interceptors: { request: { use: () => {} }, response: { use: () => {} } },
};

export const setSecureToken = jest.fn();
export const clearSecureTokens = jest.fn();
export const getSecureToken = jest.fn(() => null);
export const getSecureRefreshToken = jest.fn(() => null);
export const endpoints = { analysis: { availableModels: '/available-models', orchestrator: '/orchestrator/analyze', analyze: '/analyze' } };

export default mockApi;



