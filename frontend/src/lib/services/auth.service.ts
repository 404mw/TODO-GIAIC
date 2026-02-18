import { apiClient } from '@/lib/api/client';
import {
  GoogleOAuthCallbackSchema,
  GoogleAuthResponseSchema,
  RefreshTokenRequestSchema,
  RefreshTokenResponseSchema,
  LogoutRequestSchema,
  type GoogleOAuthCallback,
  type GoogleAuthResponse,
  type RefreshTokenRequest,
  type RefreshTokenResponse,
  type LogoutRequest,
} from '@/lib/schemas/auth.schema';

/**
 * Authentication Service
 * Handles Google OAuth, token refresh, and logout operations
 * API.md: Authentication Endpoints
 */
export const authService = {
  /**
   * Exchange Google ID token for backend JWT tokens
   * API.md: POST /api/v1/auth/google/callback
   *
   * @param idToken - Google ID token from OAuth flow
   * @returns Access token, refresh token, and user profile
   * @throws ApiError with code UNAUTHORIZED if Google token is invalid
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests
   *
   * @example
   * ```ts
   * const response = await authService.googleCallback('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...');
   * localStorage.setItem('auth_token', response.access_token);
   * localStorage.setItem('refresh_token', response.refresh_token);
   * ```
   */
  async googleCallback(idToken: string): Promise<GoogleAuthResponse> {
    const request: GoogleOAuthCallback = { id_token: idToken };

    // Validate request schema
    GoogleOAuthCallbackSchema.parse(request);

    // Call API and validate response
    const response = await apiClient.post<GoogleAuthResponse>(
      '/auth/google/callback',
      request,
      GoogleAuthResponseSchema
    );

    return response;
  },

  /**
   * Exchange refresh token for new access and refresh tokens
   * API.md: POST /api/v1/auth/refresh
   *
   * @param refreshToken - Opaque refresh token (7-day expiry)
   * @returns New access token and refresh token (old token revoked)
   * @throws ApiError with code INVALID_REFRESH_TOKEN if token is invalid or expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests
   *
   * @example
   * ```ts
   * const refreshToken = localStorage.getItem('refresh_token');
   * const response = await authService.refreshTokens(refreshToken);
   * localStorage.setItem('auth_token', response.access_token);
   * localStorage.setItem('refresh_token', response.refresh_token);
   * ```
   *
   * @note Refresh tokens are single-use. The old token is revoked when new one is issued.
   */
  async refreshTokens(refreshToken: string): Promise<RefreshTokenResponse> {
    const request: RefreshTokenRequest = { refresh_token: refreshToken };

    // Validate request schema
    RefreshTokenRequestSchema.parse(request);

    // Call API and validate response
    const response = await apiClient.post<RefreshTokenResponse>(
      '/auth/refresh',
      request,
      RefreshTokenResponseSchema
    );

    return response;
  },

  /**
   * Revoke refresh token and end session
   * API.md: POST /api/v1/auth/logout
   *
   * @param refreshToken - Opaque refresh token to revoke
   * @returns void (204 No Content)
   * @throws ApiError with code INVALID_REFRESH_TOKEN if token is invalid
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests
   *
   * @example
   * ```ts
   * const refreshToken = localStorage.getItem('refresh_token');
   * await authService.logout(refreshToken);
   * localStorage.removeItem('auth_token');
   * localStorage.removeItem('refresh_token');
   * ```
   */
  async logout(refreshToken: string): Promise<void> {
    const request: LogoutRequest = { refresh_token: refreshToken };

    // Validate request schema
    LogoutRequestSchema.parse(request);

    // Call API (no response body - 204 No Content)
    await apiClient.post<void>(
      '/auth/logout',
      request
    );
  },
};
