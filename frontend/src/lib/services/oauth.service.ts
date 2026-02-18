/**
 * OAuth Service
 *
 * Handles Google OAuth authentication using Google Sign-In SDK
 * Sends ID tokens to backend for verification and JWT generation
 * Per API.md: POST /api/v1/auth/google/callback
 */

import { apiClient } from '@/lib/api/client'
import { GoogleAuthResponseSchema } from '@/lib/schemas/auth.schema'

/**
 * OAuth Service
 * Manages Google Sign-In authentication using ID tokens
 */
export const oauthService = {
  /**
   * Authenticate with Google using ID token from Google Sign-In SDK
   * Sends Google ID token to backend for verification and JWT generation
   * Per API.md: POST /api/v1/auth/google/callback
   *
   * @param idToken - Google ID token from Google Sign-In SDK
   * @returns Promise with access token, refresh token, and user data
   */
  async authenticateWithGoogle(idToken: string) {
    try {
      const response = await apiClient.post(
        '/auth/google/callback',
        { id_token: idToken },
        GoogleAuthResponseSchema
      )

      console.log('✅ Auth response received:', {
        hasAccessToken: !!response.access_token,
        hasRefreshToken: !!response.refresh_token,
        hasUser: !!response.user,
      })

      // Store tokens in localStorage
      if (response.access_token) {
        localStorage.setItem('auth_token', response.access_token)
        console.log('✅ Stored auth_token in localStorage')
      } else {
        console.error('❌ No access_token in response!')
      }

      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token)
        console.log('✅ Stored refresh_token in localStorage')
      } else {
        console.error('❌ No refresh_token in response!')
      }

      return response
    } catch (error) {
      console.error('Google authentication failed:', error)
      throw new Error('Failed to authenticate with Google')
    }
  },
}
