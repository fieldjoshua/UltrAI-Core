import apiClient, {
  setSecureToken,
  clearSecureTokens,
  getSecureToken,
} from './api';

// Auth types
export interface User {
  id: number;
  email: string;
  username?: string;
  role: string;
  subscription_tier: string;
  account_balance: number;
  is_verified: boolean;
  full_name?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email_or_username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface UserBalance {
  balance: number;
  currency: string;
}

export interface Transaction {
  id: number;
  type: 'credit' | 'debit';
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  metadata?: Record<string, any>;
  created_at: string;
}

class AuthService {
  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!getSecureToken();
  }

  // Login user
  async login(credentials: LoginCredentials): Promise<User> {
    try {
      const response = await apiClient.post<AuthResponse>(
        '/auth/login',
        credentials
      );

      // Store the token securely
      setSecureToken(response.data.access_token);

      return response.data.user;
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.response?.data?.message) {
        throw new Error(error.response.data.message);
      }
      throw new Error('Login failed. Please check your credentials.');
    }
  }

  // Register new user
  async register(data: RegisterData): Promise<User> {
    try {
      const response = await apiClient.post<User>('/auth/register', data);
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error);
      if (error.response?.data?.message) {
        throw new Error(error.response.data.message);
      }
      if (error.response?.data?.details) {
        const details = error.response.data.details;
        if (Array.isArray(details) && details.length > 0) {
          throw new Error(details[0].msg || 'Validation error');
        }
      }
      throw new Error('Registration failed. Please try again.');
    }
  }

  // Get current user info
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    } catch (error: any) {
      console.error('Get current user error:', error);
      if (error.response?.status === 401) {
        // Token might be invalid
        clearSecureTokens();
        throw new Error('Session expired. Please log in again.');
      }
      throw new Error('Failed to fetch user information.');
    }
  }

  // Get user balance
  async getBalance(): Promise<UserBalance> {
    try {
      const response = await apiClient.get<UserBalance>('/user/balance');
      return response.data;
    } catch (error: any) {
      console.error('Get balance error:', error);
      throw new Error('Failed to fetch balance.');
    }
  }

  // Get transaction history
  async getTransactions(
    limit: number = 50,
    offset: number = 0
  ): Promise<Transaction[]> {
    try {
      const response = await apiClient.get<{ transactions: Transaction[] }>(
        '/user/transactions',
        {
          params: { limit, offset },
        }
      );
      return response.data.transactions;
    } catch (error: any) {
      console.error('Get transactions error:', error);
      throw new Error('Failed to fetch transactions.');
    }
  }

  // Logout user
  logout(): void {
    clearSecureTokens();
    // Optionally call logout endpoint to invalidate token on server
    apiClient.post('/auth/logout').catch(err => {
      console.error('Logout endpoint error:', err);
    });
  }

  // Update user profile
  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.put<User>('/auth/profile', data);
      return response.data;
    } catch (error: any) {
      console.error('Update profile error:', error);
      throw new Error('Failed to update profile.');
    }
  }

  // Request password reset
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await apiClient.post('/auth/forgot-password', { email });
    } catch (error: any) {
      console.error('Password reset request error:', error);
      throw new Error('Failed to send password reset email.');
    }
  }

  // Reset password with token
  async resetPassword(token: string, newPassword: string): Promise<void> {
    try {
      await apiClient.post('/auth/reset-password', {
        token,
        new_password: newPassword,
      });
    } catch (error: any) {
      console.error('Password reset error:', error);
      throw new Error('Failed to reset password.');
    }
  }

  // Verify email with token
  async verifyEmail(token: string): Promise<void> {
    try {
      await apiClient.post('/auth/verify-email', { token });
    } catch (error: any) {
      console.error('Email verification error:', error);
      throw new Error('Failed to verify email.');
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
