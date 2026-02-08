/**
 * Auth Flow Integration Tests
 *
 * Tests the authentication lifecycle:
 * 1. Google OAuth → token exchange → user session
 * 2. Token refresh on 401
 * 3. Logout clears session
 * 4. Unauthenticated redirect
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { AuthProvider, useAuth } from '@/lib/contexts/AuthContext'

// Mock API modules
jest.mock('@/lib/api/user', () => ({
  getCurrentUser: jest.fn(),
}))

jest.mock('@/lib/api/auth', () => ({
  exchangeGoogleToken: jest.fn(),
  refreshAccessToken: jest.fn(),
  logout: jest.fn(),
}))

jest.mock('@/lib/api/token', () => ({
  hasValidAccessToken: jest.fn(),
  getRefreshToken: jest.fn(),
  getAccessToken: jest.fn(),
  clearTokens: jest.fn(),
  setTokens: jest.fn(),
}))

// Import mocked modules
import { getCurrentUser } from '@/lib/api/user'
import { exchangeGoogleToken, refreshAccessToken, logout } from '@/lib/api/auth'
import { hasValidAccessToken, getRefreshToken, clearTokens } from '@/lib/api/token'

const mockGetCurrentUser = getCurrentUser as jest.MockedFunction<typeof getCurrentUser>
const mockExchangeGoogleToken = exchangeGoogleToken as jest.MockedFunction<typeof exchangeGoogleToken>
const mockRefreshAccessToken = refreshAccessToken as jest.MockedFunction<typeof refreshAccessToken>
const mockLogout = logout as jest.MockedFunction<typeof logout>
const mockHasValidAccessToken = hasValidAccessToken as jest.MockedFunction<typeof hasValidAccessToken>
const mockGetRefreshToken = getRefreshToken as jest.MockedFunction<typeof getRefreshToken>
const mockClearTokens = clearTokens as jest.MockedFunction<typeof clearTokens>

const testUser = {
  id: '00000000-0000-4000-a000-000000000001',
  email: 'test@example.com',
  name: 'Test User',
  timezone: 'UTC',
  tier: 'free' as const,
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-06-01T00:00:00Z',
}

/** Helper component that renders auth state */
function AuthStatus() {
  const { user, isAuthenticated, isLoading, error } = useAuth()
  return (
    <div>
      <span data-testid="loading">{isLoading ? 'loading' : 'ready'}</span>
      <span data-testid="authenticated">{isAuthenticated ? 'yes' : 'no'}</span>
      <span data-testid="user">{user?.email ?? 'none'}</span>
      <span data-testid="error">{error?.message ?? 'none'}</span>
    </div>
  )
}

/** Helper component with login/logout buttons */
function AuthActions() {
  const { handleGoogleCallback, logout: doLogout, isAuthenticated, user } = useAuth()
  return (
    <div>
      <span data-testid="auth-user">{user?.email ?? 'none'}</span>
      <span data-testid="auth-status">{isAuthenticated ? 'yes' : 'no'}</span>
      <button onClick={() => handleGoogleCallback('test-id-token')}>Login</button>
      <button onClick={() => doLogout()}>Logout</button>
    </div>
  )
}

function renderWithAuth(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    createElement(
      QueryClientProvider,
      { client: queryClient },
      createElement(AuthProvider, null, ui)
    )
  )
}

describe('Auth Flow Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Default: no tokens, no session
    mockHasValidAccessToken.mockReturnValue(false)
    mockGetRefreshToken.mockReturnValue(null)

    // Prevent actual redirects
    delete (window as any).location
    ;(window as any).location = { href: '/', origin: 'http://localhost:3000' }
  })

  describe('1. Google OAuth → token exchange → user session', () => {
    it('should establish user session after Google callback', async () => {
      mockExchangeGoogleToken.mockResolvedValue({
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        expires_in: 3600,
        token_type: 'Bearer',
      })
      mockGetCurrentUser.mockResolvedValue(testUser)

      renderWithAuth(createElement(AuthActions))

      // Initially no session
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('no')
      })

      // Simulate Google OAuth callback
      const loginButton = screen.getByText('Login')
      await act(async () => {
        await userEvent.click(loginButton)
      })

      // User session should be established
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('yes')
        expect(screen.getByTestId('auth-user')).toHaveTextContent('test@example.com')
      })

      expect(mockExchangeGoogleToken).toHaveBeenCalledWith('test-id-token')
      expect(mockGetCurrentUser).toHaveBeenCalled()
    })
  })

  describe('2. Token refresh on expired access token', () => {
    it('should refresh token and fetch user on mount when access token is expired', async () => {
      // Access token expired but refresh token available
      mockHasValidAccessToken.mockReturnValue(false)
      mockGetRefreshToken.mockReturnValue('valid-refresh-token')
      mockRefreshAccessToken.mockResolvedValue({
        access_token: 'refreshed-access',
        refresh_token: 'refreshed-refresh',
        expires_in: 3600,
        token_type: 'Bearer',
      })
      mockGetCurrentUser.mockResolvedValue(testUser)

      renderWithAuth(createElement(AuthStatus))

      // Should eventually load user after refresh
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes')
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })

      expect(mockRefreshAccessToken).toHaveBeenCalled()
      expect(mockGetCurrentUser).toHaveBeenCalled()
    })

    it('should clear tokens when refresh fails', async () => {
      mockHasValidAccessToken.mockReturnValue(false)
      mockGetRefreshToken.mockReturnValue('expired-refresh-token')
      mockRefreshAccessToken.mockRejectedValue(new Error('Refresh failed'))

      renderWithAuth(createElement(AuthStatus))

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no')
      })

      expect(mockClearTokens).toHaveBeenCalled()
    })
  })

  describe('3. Logout clears session', () => {
    it('should clear user state and cached data on logout', async () => {
      // Start with valid session
      mockHasValidAccessToken.mockReturnValue(true)
      mockGetCurrentUser.mockResolvedValue(testUser)
      mockLogout.mockResolvedValue(undefined)

      renderWithAuth(createElement(AuthActions))

      // Wait for session to be established
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('yes')
      })

      // Click logout
      const logoutButton = screen.getByText('Logout')
      await act(async () => {
        await userEvent.click(logoutButton)
      })

      // Session should be cleared
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('no')
        expect(screen.getByTestId('auth-user')).toHaveTextContent('none')
      })

      expect(mockLogout).toHaveBeenCalled()
    })
  })

  describe('4. Unauthenticated state', () => {
    it('should show unauthenticated when no tokens exist', async () => {
      mockHasValidAccessToken.mockReturnValue(false)
      mockGetRefreshToken.mockReturnValue(null)

      renderWithAuth(createElement(AuthStatus))

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no')
        expect(screen.getByTestId('user')).toHaveTextContent('none')
      })
    })

    it('should load user on mount when access token is valid', async () => {
      mockHasValidAccessToken.mockReturnValue(true)
      mockGetCurrentUser.mockResolvedValue(testUser)

      renderWithAuth(createElement(AuthStatus))

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes')
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })
    })
  })
})
