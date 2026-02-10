import { z } from 'zod';
import { UserTierSchema } from './common.schema';

/**
 * User schema matching backend User model.
 * Per data-model.md Entity 1
 */
export const UserSchema = z.object({
  id: z.string().uuid(),

  // OAuth fields
  google_id: z.string(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  avatar_url: z.string().nullable(),

  // Preferences
  timezone: z.string().default('UTC'),
  tier: UserTierSchema.default('free'),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Public user profile schema
 */
export const UserPublicSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  avatar_url: z.string().nullable(),
});

/**
 * Request schema for updating user profile (FR-070)
 */
export const UpdateUserRequestSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  timezone: z.string().optional(),
});

// Type exports
export type User = z.infer<typeof UserSchema>;
export type UserPublic = z.infer<typeof UserPublicSchema>;
export type UpdateUserRequest = z.infer<typeof UpdateUserRequestSchema>;
