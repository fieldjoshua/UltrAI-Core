import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { jest } from '@jest/globals';

// Mock API client to avoid importing real module that references import.meta.env
jest.mock('@/services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
    interceptors: { request: { use: () => {} }, response: { use: () => {} } },
  },
  setSecureToken: jest.fn(),
  clearSecureTokens: jest.fn(),
  getSecureToken: jest.fn().mockReturnValue(null),
  getSecureRefreshToken: jest.fn().mockReturnValue(null),
  endpoints: {
    analysis: {
      availableModels: '/available-models',
      orchestrator: '/orchestrator/analyze',
      analyze: '/analyze',
    },
  },
}));
// Also mock relative path variants that may be used internally
jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
    interceptors: { request: { use: () => {} }, response: { use: () => {} } },
  },
  setSecureToken: jest.fn(),
  clearSecureTokens: jest.fn(),
  getSecureToken: jest.fn().mockReturnValue(null),
  getSecureRefreshToken: jest.fn().mockReturnValue(null),
  endpoints: {
    analysis: {
      availableModels: '/available-models',
      orchestrator: '/orchestrator/analyze',
      analyze: '/analyze',
    },
  },
}));
// Mock auth store to avoid pulling actual authService
jest.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    login: jest.fn().mockResolvedValue(undefined),
    isLoading: false,
    error: null,
    clearError: jest.fn(),
  }),
}));
jest.mock('../../stores/authStore', () => ({
  useAuthStore: () => ({
    login: jest.fn().mockResolvedValue(undefined),
    isLoading: false,
    error: null,
    clearError: jest.fn(),
  }),
}));

// Mock authService to avoid importing api.ts indirectly
jest.mock('@/services/authService', () => ({
  __esModule: true,
  authService: {
    login: jest.fn().mockResolvedValue({
      id: 1,
      email: 'test@example.com',
      role: 'user',
      subscription_tier: 'free',
      account_balance: 0,
      is_verified: true,
      created_at: '',
      updated_at: '',
    }),
  },
}));
jest.mock('../../services/authService', () => ({
  __esModule: true,
  authService: {
    login: jest.fn().mockResolvedValue({
      id: 1,
      email: 'test@example.com',
      role: 'user',
      subscription_tier: 'free',
      account_balance: 0,
      is_verified: true,
      created_at: '',
      updated_at: '',
    }),
  },
}));

// Import after mocks
import { LoginPage } from '@/pages/LoginPage';

describe('LoginPage', () => {
  it('shows registration success alert when registered=true', () => {
    render(
      <MemoryRouter
        initialEntries={[{ pathname: '/login', search: '?registered=true' }]}
      >
        <Routes>
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(
      screen.getByText(
        /Registration successful! Please log in with your new account./i
      )
    ).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });
});
