'use client';

import { createContext, useState, useEffect, ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import type { User } from '@/lib/schemas/user.schema';
import { authService } from '@/lib/services/auth.service';
import { usersService } from '@/lib/services/users.service';
import { ApiError } from '@/lib/api/client';

interface AuthContextType {
  user: User | null;
  logout: () => Promise<void>;
  refetch: () => Promise<void>;
  refreshTokenIfNeeded: () => Promise<void>;
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
  const pathname = usePathname();

  useEffect(() => {
    // Only fetch user on protected routes (dashboard, app)
    // Skip public routes (landing page, about, pricing, etc.)
    const isProtectedRoute = pathname?.startsWith('/dashboard') || pathname?.startsWith('/app');

    if (!isProtectedRoute) {
      setIsLoading(false);
      return;
    }

    // Restore session on mount for protected routes
    const token = localStorage.getItem('auth_token');
    if (token) {
      fetchCurrentUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [pathname]);

  async function fetchCurrentUser() {
    try {
      // Use new users service with proper response unwrapping
      const response = await usersService.getCurrentUser();
      setUser(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch current user:', err);

      // Handle token expiration
      if (err instanceof ApiError && err.code === 'TOKEN_EXPIRED') {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            await refreshTokens(refreshToken);
            // Retry fetching user after refresh
            const response = await usersService.getCurrentUser();
            setUser(response.data);
            setError(null);
            return;
          } catch (refreshErr) {
            console.error('Token refresh failed:', refreshErr);
          }
        }
      }

      // Clear tokens and user on error
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      // Don't set error here - this is silent background refresh
    }
  }

  async function refreshTokens(refreshToken: string) {
    try {
      const response = await authService.refreshTokens(refreshToken);

      // Store new tokens (refresh token rotation)
      // Note: Auth responses are NOT wrapped with DataResponse
      localStorage.setItem('auth_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);

      console.log('✅ Tokens refreshed successfully');
    } catch (err) {
      console.error('Failed to refresh tokens:', err);
      // Clear tokens on refresh failure
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      throw err;
    }
  }

  async function refreshTokenIfNeeded() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await refreshTokens(refreshToken);
    }
  }

  async function logout() {
    const refreshToken = localStorage.getItem('refresh_token');

    // Call backend logout if we have a refresh token
    if (refreshToken) {
      try {
        await authService.logout(refreshToken);
      } catch (err) {
        console.error('Logout API call failed:', err);
        // Continue with local cleanup even if API call fails
      }
    }

    // Clear local storage and state
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
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
        logout,
        refetch,
        refreshTokenIfNeeded,
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
