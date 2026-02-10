import { z } from 'zod';

/**
 * Login Request schema
 */
export const LoginRequestSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

/**
 * Register Request schema
 */
export const RegisterRequestSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  full_name: z.string().min(1, 'Name is required'),
});

/**
 * Auth Token response schema
 */
export const AuthTokenSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default('bearer'),
});

/**
 * Google OAuth callback schema
 */
export const GoogleOAuthCallbackSchema = z.object({
  code: z.string(),
  state: z.string().optional(),
});

// Type exports
export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type RegisterRequest = z.infer<typeof RegisterRequestSchema>;
export type AuthToken = z.infer<typeof AuthTokenSchema>;
export type GoogleOAuthCallback = z.infer<typeof GoogleOAuthCallbackSchema>;
