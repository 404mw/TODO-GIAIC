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
