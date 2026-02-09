/**
 * OAuth Service
 *
 * Handles Google OAuth authentication flow
 * Integrates with backend OAuth endpoints
 */

import { apiClient } from '@/lib/api/client'
import { z } from 'zod'

/**
 * OAuth callback response schema
 */
const OAuthCallbackResponseSchema = z.object({
  data: z.object({
    access_token: z.string(),
    token_type: z.string().default('bearer'),
    expires_in: z.number().optional(),
  }),
})

/**
 * OAuth Service
 * Manages Google OAuth authentication flow
 */
export const oauthService = {
  /**
   * Initiate Google OAuth login flow
   * Redirects user to backend OAuth initiation endpoint
   * Backend will redirect to Google for authentication
   *
   * @param redirectTo - Optional URL to redirect to after successful login
   */
  initiateGoogleLogin(redirectTo?: string): void {
    if (typeof window === 'undefined') return

    const params = new URLSearchParams()
    if (redirectTo) {
      params.append('redirect', redirectTo)
    }

    // Redirect to backend OAuth initiation endpoint
    // Backend will handle the redirect to Google
    const backendOAuthUrl = `/api/v1/auth/google/login${params.toString() ? `?${params.toString()}` : ''}`
    window.location.href = backendOAuthUrl
  },

  /**
   * Handle OAuth callback after Google redirects back
   * Exchange authorization code for access token
   *
   * @param code - Authorization code from Google
   * @param state - Optional state parameter for CSRF protection
   * @returns Access token response
   */
  async handleCallback(code: string, state?: string): Promise<{ access_token: string }> {
    try {
      const response = await apiClient.post(
        '/auth/google/callback',
        { code, state },
        OAuthCallbackResponseSchema
      )

      // Store token in localStorage
      localStorage.setItem('auth_token', response.data.access_token)

      return {
        access_token: response.data.access_token,
      }
    } catch (error) {
      console.error('OAuth callback failed:', error)
      throw new Error('Failed to complete Google sign-in')
    }
  },

  /**
   * Check if user is redirected from OAuth flow
   * @returns Boolean indicating if current URL contains OAuth callback parameters
   */
  isOAuthCallback(): boolean {
    if (typeof window === 'undefined') return false

    const params = new URLSearchParams(window.location.search)
    return params.has('code') && params.has('state')
  },

  /**
   * Get OAuth callback parameters from URL
   * @returns Object with code and state if present
   */
  getCallbackParams(): { code: string; state: string } | null {
    if (typeof window === 'undefined') return null

    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const state = params.get('state')

    if (code && state) {
      return { code, state }
    }

    return null
  },

  /**
   * Clear OAuth parameters from URL
   * Useful after handling callback to clean up URL
   */
  clearCallbackParams(): void {
    if (typeof window === 'undefined') return

    const url = new URL(window.location.href)
    url.searchParams.delete('code')
    url.searchParams.delete('state')
    window.history.replaceState({}, document.title, url.toString())
  },
}

/**
 * Helper function to build redirect URL
 * Constructs the full redirect URL for OAuth callback
 *
 * @param path - Path to redirect to after login (default: /dashboard)
 * @returns Full redirect URL
 */
export function buildOAuthRedirectUrl(path: string = '/dashboard'): string {
  if (typeof window === 'undefined') {
    return path
  }

  return `${window.location.origin}${path}`
}

/**
 * OAuth error types
 */
export enum OAuthError {
  CANCELLED = 'oauth_cancelled',
  FAILED = 'oauth_failed',
  NETWORK_ERROR = 'network_error',
  INVALID_STATE = 'invalid_state',
}

/**
 * Parse OAuth error from URL parameters
 * @returns Error type or null if no error
 */
export function getOAuthError(): OAuthError | null {
  if (typeof window === 'undefined') return null

  const params = new URLSearchParams(window.location.search)
  const error = params.get('error')

  switch (error) {
    case 'access_denied':
      return OAuthError.CANCELLED
    case 'invalid_state':
      return OAuthError.INVALID_STATE
    case 'server_error':
      return OAuthError.FAILED
    default:
      return null
  }
}
