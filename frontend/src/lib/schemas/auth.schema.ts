import { z } from 'zod';
import { UserSchema } from './user.schema';

/**
 * Google OAuth callback request schema
 * API.md: POST /api/v1/auth/google/callback
 */
export const GoogleOAuthCallbackSchema = z.object({
  id_token: z.string(),
});

/**
 * Google authentication response schema
 * API.md: POST /api/v1/auth/google/callback
 * Returns access token, refresh token, and user profile
 */
export const GoogleAuthResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  expires_in: z.number().int().positive(),
  user: UserSchema.pick({
    id: true,
    email: true,
    name: true,
    avatar_url: true,
    tier: true,
    created_at: true,
  }),
});

/**
 * Refresh token request schema
 * API.md: POST /api/v1/auth/refresh
 */
export const RefreshTokenRequestSchema = z.object({
  refresh_token: z.string(),
});

/**
 * Refresh token response schema
 * API.md: POST /api/v1/auth/refresh
 * Note: Refresh tokens are single-use (old token revoked when new one issued)
 */
export const RefreshTokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  expires_in: z.number().int().positive(),
});

/**
 * Logout request schema
 * API.md: POST /api/v1/auth/logout
 * Revokes refresh token and ends session (returns 204 No Content)
 */
export const LogoutRequestSchema = z.object({
  refresh_token: z.string(),
});

// Type exports
export type GoogleOAuthCallback = z.infer<typeof GoogleOAuthCallbackSchema>;
export type GoogleAuthResponse = z.infer<typeof GoogleAuthResponseSchema>;
export type RefreshTokenRequest = z.infer<typeof RefreshTokenRequestSchema>;
export type RefreshTokenResponse = z.infer<typeof RefreshTokenResponseSchema>;
export type LogoutRequest = z.infer<typeof LogoutRequestSchema>;
