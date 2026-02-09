'use client';

import { createContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api/client';
import { AuthTokenSchema, LoginRequestSchema, type LoginRequest } from '@/lib/schemas/auth.schema';
import type { User } from '@/lib/schemas/user.schema';
import { oauthService } from '@/lib/services/oauth.service';
import { z } from 'zod';

const UserResponseSchema = z.object({
  data: z.object({
    id: z.string().uuid(),
    email: z.string().email(),
    full_name: z.string(),
    is_active: z.boolean(),
    tier: z.enum(['free', 'pro']).default('free'),
    created_at: z.string(),
    updated_at: z.string().optional(),
  }),
});

interface AuthContextType {
  user: User | null;
  login: (credentials: LoginRequest) => Promise<void>;
  loginWithGoogle: (redirectTo?: string) => void;
  logout: () => void;
  refetch: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Restore session on mount
    const token = localStorage.getItem('auth_token');
    if (token) {
      fetchCurrentUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  async function fetchCurrentUser() {
    try {
      const response = await apiClient.get('/users/me', UserResponseSchema);
      // Map API response to User type
      const mappedUser: User = {
        id: response.data.id,
        google_id: '', // Not returned by API, will be populated during OAuth
        email: response.data.email,
        name: response.data.full_name,
        avatar_url: null, // Not returned by API
        timezone: 'UTC', // Default timezone
        tier: response.data.tier,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at || response.data.created_at,
      };
      setUser(mappedUser);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch current user:', err);
      localStorage.removeItem('auth_token');
      setUser(null);
      // Don't set error here - this is silent background refresh
    }
  }

  async function login(credentials: LoginRequest) {
    try {
      setIsLoading(true);
      setError(null);

      // Validate credentials
      const validatedCredentials = LoginRequestSchema.parse(credentials);

      // Get auth token
      const tokenResponse = await apiClient.post(
        '/auth/login',
        validatedCredentials,
        AuthTokenSchema
      );

      // Store token
      localStorage.setItem('auth_token', tokenResponse.access_token);

      // Fetch user details
      await fetchCurrentUser();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err; // Re-throw so UI can handle
    } finally {
      setIsLoading(false);
    }
  }

  function loginWithGoogle(redirectTo?: string) {
    try {
      setError(null);
      oauthService.initiateGoogleLogin(redirectTo);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initiate Google login';
      setError(errorMessage);
    }
  }

  function logout() {
    localStorage.removeItem('auth_token');
    setUser(null);
    setError(null);
  }

  async function refetch() {
    await fetchCurrentUser();
  }

  function clearError() {
    setError(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        loginWithGoogle,
        logout,
        refetch,
        isAuthenticated: !!user,
        isLoading,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
