import { z } from 'zod';

/**
 * Focus Session schema matching backend FocusSession model.
 * Phase 16: User Story 12 - Focus Mode Tracking (FR-045)
 */
export const FocusSessionSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  task_id: z.string().uuid(),

  // Session timing
  started_at: z.string().datetime(),
  ended_at: z.string().datetime().nullable(),
  duration_seconds: z.number().int().min(0).nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Request schema for starting a focus session
 */
export const StartFocusSessionRequestSchema = z.object({
  task_id: z.string().uuid(),
});

/**
 * Request schema for ending a focus session
 */
export const EndFocusSessionRequestSchema = z.object({
  session_id: z.string().uuid(),
});

// Type exports
export type FocusSession = z.infer<typeof FocusSessionSchema>;
export type StartFocusSessionRequest = z.infer<typeof StartFocusSessionRequestSchema>;
export type EndFocusSessionRequest = z.infer<typeof EndFocusSessionRequestSchema>;
