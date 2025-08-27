import { create } from 'zustand';
import { authService, User } from '../services/authService';
import { clearSecureTokens } from '../services/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, username?: string, fullName?: string) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: authService.isAuthenticated(),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const user = await authService.login({ 
        email_or_username: email, 
        password 
      });
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Login failed',
        isAuthenticated: false,
        user: null
      });
      throw error;
    }
  },

  register: async (email: string, password: string, username?: string, fullName?: string) => {
    set({ isLoading: true, error: null });
    try {
      const user = await authService.register({
        email,
        password,
        username,
        full_name: fullName
      });
      set({ 
        user, 
        isAuthenticated: false, // User needs to login after registration
        isLoading: false,
        error: null 
      });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Registration failed',
      });
      throw error;
    }
  },

  logout: () => {
    authService.logout();
    set({ 
      user: null, 
      isAuthenticated: false, 
      error: null 
    });
  },

  fetchCurrentUser: async () => {
    if (!authService.isAuthenticated()) {
      set({ user: null, isAuthenticated: false });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authService.getCurrentUser();
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false,
        error: null
      });
    } catch (error: any) {
      set({ 
        user: null, 
        isAuthenticated: false, 
        isLoading: false,
        error: error.message
      });
      // If token is invalid, clear it
      if (error.message.includes('expired')) {
        clearSecureTokens();
      }
    }
  },

  clearError: () => set({ error: null }),

  setUser: (user: User | null) => set({ 
    user, 
    isAuthenticated: !!user 
  }),
}));