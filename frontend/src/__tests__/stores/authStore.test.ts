import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuthStore } from '../../stores/authStore';
import * as authApi from '../../api/auth';
import axios from 'axios';

// Mock dependencies
import { jest } from '@jest/globals';
jest.mock('../../api/auth');
jest.mock('axios');

describe('authStore', () => {
  // Helper to get current store state
  const getStoreState = () => {
    const { result } = renderHook(() => useAuthStore());
    return result.current;
  };

  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });

    // Clear mocks
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    const mockLoginData = {
      email: 'test@example.com',
      password: 'password123',
    };

    const mockLoginResponse = {
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      },
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'Bearer',
    };

    it('should successfully log in a user', async () => {
      (authApi.login as jest.Mock).mockResolvedValueOnce(mockLoginResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login(mockLoginData.email, mockLoginData.password);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockLoginResponse.user);
      expect(result.current.token).toBe(mockLoginResponse.access_token);
      expect(result.current.refreshToken).toBe(mockLoginResponse.refresh_token);
      expect(result.current.error).toBeNull();
    });

    it('should store tokens in localStorage', async () => {
      (authApi.login as jest.Mock).mockResolvedValueOnce(mockLoginResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login(mockLoginData.email, mockLoginData.password);
      });

      expect(localStorage.getItem('access_token')).toBe(mockLoginResponse.access_token);
      expect(localStorage.getItem('refresh_token')).toBe(mockLoginResponse.refresh_token);
    });

    it('should set axios default authorization header', async () => {
      (authApi.login as jest.Mock).mockResolvedValueOnce(mockLoginResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login(mockLoginData.email, mockLoginData.password);
      });

      expect(axios.defaults.headers.common['Authorization']).toBe(
        `Bearer ${mockLoginResponse.access_token}`
      );
    });

    it('should handle login errors', async () => {
      const errorMessage = 'Invalid credentials';
      (authApi.login as jest.Mock).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.login(mockLoginData.email, mockLoginData.password);
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.error).toBe(errorMessage);
    });

    it('should set loading state during login', async () => {
      let resolveLogin: (value: any) => void;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });

      (authApi.login as jest.Mock).mockReturnValueOnce(loginPromise);

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.login(mockLoginData.email, mockLoginData.password);
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        resolveLogin!(mockLoginResponse);
        await loginPromise;
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('logout', () => {
    beforeEach(() => {
      // Set up authenticated state
      useAuthStore.setState({
        user: { id: '123', email: 'test@example.com' },
        token: 'mock-token',
        refreshToken: 'mock-refresh-token',
        isAuthenticated: true,
      });

      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('refresh_token', 'mock-refresh-token');
      axios.defaults.headers.common['Authorization'] = 'Bearer mock-token';
    });

    it('should clear user state on logout', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.refreshToken).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('should clear tokens from localStorage', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.logout();
      });

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });

    it('should remove axios authorization header', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.logout();
      });

      expect(axios.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });

  describe('register', () => {
    const mockRegisterData = {
      email: 'newuser@example.com',
      password: 'password123',
      name: 'New User',
    };

    const mockRegisterResponse = {
      user: {
        id: '456',
        email: 'newuser@example.com',
        name: 'New User',
      },
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
      token_type: 'Bearer',
    };

    it('should successfully register a new user', async () => {
      (authApi.register as jest.Mock).mockResolvedValueOnce(mockRegisterResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.register(
          mockRegisterData.email,
          mockRegisterData.password,
          mockRegisterData.name
        );
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockRegisterResponse.user);
      expect(result.current.token).toBe(mockRegisterResponse.access_token);
    });

    it('should handle registration errors', async () => {
      const errorMessage = 'Email already exists';
      (authApi.register as jest.Mock).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.register(
          mockRegisterData.email,
          mockRegisterData.password,
          mockRegisterData.name
        );
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });
  });

  describe('refreshAccessToken', () => {
    const mockRefreshResponse = {
      access_token: 'new-access-token',
      token_type: 'Bearer',
    };

    beforeEach(() => {
      useAuthStore.setState({
        refreshToken: 'valid-refresh-token',
      });
    });

    it('should refresh access token successfully', async () => {
      (authApi.refreshToken as jest.Mock).mockResolvedValueOnce(mockRefreshResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.refreshAccessToken();
      });

      expect(result.current.token).toBe(mockRefreshResponse.access_token);
      expect(localStorage.getItem('access_token')).toBe(mockRefreshResponse.access_token);
      expect(axios.defaults.headers.common['Authorization']).toBe(
        `Bearer ${mockRefreshResponse.access_token}`
      );
    });

    it('should logout if refresh token is missing', async () => {
      useAuthStore.setState({ refreshToken: null });

      const { result } = renderHook(() => useAuthStore());
      const logoutSpy = jest.spyOn(result.current, 'logout');

      await act(async () => {
        await result.current.refreshAccessToken();
      });

      expect(logoutSpy).toHaveBeenCalled();
    });

    it('should logout if refresh fails', async () => {
      (authApi.refreshToken as jest.Mock).mockRejectedValueOnce(new Error('Invalid refresh token'));

      const { result } = renderHook(() => useAuthStore());
      const logoutSpy = jest.spyOn(result.current, 'logout');

      await act(async () => {
        await result.current.refreshAccessToken();
      });

      expect(logoutSpy).toHaveBeenCalled();
    });
  });

  describe('fetchCurrentUser', () => {
    const mockUserResponse = {
      id: '123',
      email: 'test@example.com',
      name: 'Test User',
    };

    it('should fetch current user when token exists', async () => {
      localStorage.setItem('access_token', 'valid-token');
      (authApi.getCurrentUser as jest.Mock).mockResolvedValueOnce(mockUserResponse);

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.fetchCurrentUser();
      });

      expect(result.current.user).toEqual(mockUserResponse);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.token).toBe('valid-token');
    });

    it('should not fetch user when no token exists', async () => {
      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.fetchCurrentUser();
      });

      expect(authApi.getCurrentUser).not.toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('should handle fetch user errors silently', async () => {
      localStorage.setItem('access_token', 'valid-token');
      (authApi.getCurrentUser as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuthStore());

      await act(async () => {
        await result.current.fetchCurrentUser();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBeNull(); // Errors are logged but not stored
    });
  });

  describe('clearError', () => {
    it('should clear error state', () => {
      useAuthStore.setState({ error: 'Some error' });

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('initialization', () => {
    it('should load tokens from localStorage on initialization', () => {
      localStorage.setItem('access_token', 'stored-token');
      localStorage.setItem('refresh_token', 'stored-refresh-token');

      // Force re-initialization by clearing and re-importing the store
      jest.resetModules();
      const { useAuthStore: freshAuthStore } = require('../../stores/authStore');

      const { result } = renderHook(() => freshAuthStore());

      expect(result.current.token).toBe('stored-token');
      expect(result.current.refreshToken).toBe('stored-refresh-token');
    });

    it('should set axios headers if token exists on initialization', () => {
      localStorage.setItem('access_token', 'stored-token');

      jest.resetModules();
      const { useAuthStore: freshAuthStore } = require('../../stores/authStore');

      renderHook(() => freshAuthStore());

      expect(axios.defaults.headers.common['Authorization']).toBe('Bearer stored-token');
    });
  });
});