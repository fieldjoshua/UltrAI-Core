import axios from 'axios';

// @ts-ignore
const API_URL = (globalThis.import?.meta?.env?.VITE_API_URL) || 'http://localhost:8000/api';

export interface LoginResponse {
  user: {
    id: string;
    email: string;
    name?: string;
  };
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterResponse extends LoginResponse {}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await axios.post(`${API_URL}/auth/login`, {
    email,
    password,
  });
  return response.data;
}

export async function register(email: string, password: string, name?: string): Promise<RegisterResponse> {
  const response = await axios.post(`${API_URL}/auth/register`, {
    email,
    password,
    name,
  });
  return response.data;
}

export async function refreshToken(refresh_token: string): Promise<RefreshTokenResponse> {
  const response = await axios.post(`${API_URL}/auth/refresh`, {
    refresh_token,
  });
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await axios.get(`${API_URL}/auth/me`);
  return response.data;
}

export async function logout(): Promise<void> {
  await axios.post(`${API_URL}/auth/logout`);
}