import { z } from 'zod';
import { AchievementCategorySchema, PerkTypeSchema } from './common.schema';

/**
 * Achievement Definition schema matching backend AchievementDefinition model.
 * Per data-model.md Entity 7
 */
export const AchievementDefinitionSchema = z.object({
  id: z.string(), // Achievement code (e.g., "tasks_5")

  // Achievement details
  name: z.string(),
  message: z.string(),
  category: AchievementCategorySchema,
  threshold: z.number().int().min(1),

  // Perk details
  perk_type: PerkTypeSchema.nullable(),
  perk_value: z.number().int().min(1).nullable(),
});

/**
 * User Achievement State schema matching backend UserAchievementState model.
 * Per data-model.md Entity 8
 */
export const UserAchievementStateSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Lifetime statistics
  lifetime_tasks_completed: z.number().int().min(0).default(0),

  // Streak tracking (FR-043)
  current_streak: z.number().int().min(0).default(0),
  longest_streak: z.number().int().min(0).default(0),
  last_completion_date: z.string().nullable(), // Date string (YYYY-MM-DD)

  // Focus tracking (FR-045)
  focus_completions: z.number().int().min(0).default(0),

  // Notes tracking
  notes_converted: z.number().int().min(0).default(0),

  // Unlocked achievements
  unlocked_achievements: z.array(z.string()).default([]),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Achievement Stats schema (subset of UserAchievementState)
 * Returned by /achievements/me endpoint
 */
export const AchievementStatsSchema = z.object({
  lifetime_tasks_completed: z.number().int().min(0).default(0),
  current_streak: z.number().int().min(0).default(0),
  longest_streak: z.number().int().min(0).default(0),
  focus_completions: z.number().int().min(0).default(0),
  notes_converted: z.number().int().min(0).default(0),
});

/**
 * Achievement Progress schema
 * Shows progress toward unlocking an achievement
 */
export const AchievementProgressSchema = z.object({
  id: z.string(),
  name: z.string(),
  current: z.number().int().min(0),
  threshold: z.number().int().min(1),
  unlocked: z.boolean(),
});

/**
 * Effective Limits schema
 * User's current limits based on tier and unlocked perks
 */
export const EffectiveLimitsSchema = z.object({
  max_tasks: z.number().int().min(0),
  max_notes: z.number().int().min(0),
  daily_ai_credits: z.number().int().min(0),
});

/**
 * Achievement Data Response schema
 * Complete response from /achievements/me endpoint per API.md
 */
export const AchievementDataSchema = z.object({
  stats: AchievementStatsSchema,
  unlocked: z.array(z.string()),
  progress: z.array(AchievementProgressSchema),
  effective_limits: EffectiveLimitsSchema,
});

/**
 * Achievement unlock event schema
 */
export const AchievementUnlockSchema = z.object({
  achievement_id: z.string(),
  achievement_name: z.string(),
  perk: z
    .object({
      type: PerkTypeSchema,
      value: z.number().int().min(1),
    })
    .nullable(),
});

// Type exports
export type AchievementDefinition = z.infer<typeof AchievementDefinitionSchema>;
export type UserAchievementState = z.infer<typeof UserAchievementStateSchema>;
export type AchievementUnlock = z.infer<typeof AchievementUnlockSchema>;
export type AchievementStats = z.infer<typeof AchievementStatsSchema>;
export type AchievementProgress = z.infer<typeof AchievementProgressSchema>;
export type EffectiveLimits = z.infer<typeof EffectiveLimitsSchema>;
export type AchievementData = z.infer<typeof AchievementDataSchema>;
