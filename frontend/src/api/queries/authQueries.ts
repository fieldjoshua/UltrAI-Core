import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { login, register, refreshToken, getCurrentUser, logout } from '../auth';
import { useAuthStore } from '../../stores/authStore';
import axios from 'axios';

// Query Keys
export const authKeys = {
  all: ['auth'] as const,
  user: () => [...authKeys.all, 'user'] as const,
  session: () => [...authKeys.all, 'session'] as const,
};

// Types
interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  name?: string;
}

interface AuthResponse {
  user: {
    id: string;
    email: string;
    name?: string;
  };
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Queries
export function useCurrentUser(options?: UseQueryOptions<any>) {
  const { token, setUser, setAuthenticated } = useAuthStore();
  
  return useQuery({
    queryKey: authKeys.user(),
    queryFn: getCurrentUser,
    enabled: !!token,
    onSuccess: (data) => {
      setUser(data);
      setAuthenticated(true);
    },
    onError: () => {
      setUser(null);
      setAuthenticated(false);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
}

// Mutations
export function useLogin(options?: UseMutationOptions<AuthResponse, Error, LoginCredentials>) {
  const queryClient = useQueryClient();
  const { setUser, setToken, setRefreshToken, setAuthenticated } = useAuthStore();

  return useMutation({
    mutationFn: ({ email, password }) => login(email, password),
    onSuccess: (data) => {
      // Update auth store
      setUser(data.user);
      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setAuthenticated(true);

      // Update axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;

      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);

      // Invalidate user query to refetch with new token
      queryClient.invalidateQueries({ queryKey: authKeys.user() });
    },
    ...options,
  });
}

export function useRegister(options?: UseMutationOptions<AuthResponse, Error, RegisterData>) {
  const queryClient = useQueryClient();
  const { setUser, setToken, setRefreshToken, setAuthenticated } = useAuthStore();

  return useMutation({
    mutationFn: ({ email, password, name }) => register(email, password, name),
    onSuccess: (data) => {
      // Update auth store
      setUser(data.user);
      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      setAuthenticated(true);

      // Update axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;

      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);

      // Invalidate user query
      queryClient.invalidateQueries({ queryKey: authKeys.user() });
    },
    ...options,
  });
}

export function useLogout(options?: UseMutationOptions<void, Error, void>) {
  const queryClient = useQueryClient();
  const { logout: logoutStore } = useAuthStore();

  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      // Clear auth store
      logoutStore();

      // Clear all auth queries
      queryClient.removeQueries({ queryKey: authKeys.all });
      
      // Clear all cached data
      queryClient.clear();
    },
    ...options,
  });
}

export function useRefreshToken(options?: UseMutationOptions<any, Error, string>) {
  const { setToken } = useAuthStore();

  return useMutation({
    mutationFn: refreshToken,
    onSuccess: (data) => {
      const newToken = data.access_token;
      setToken(newToken);
      localStorage.setItem('access_token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    },
    ...options,
  });
}