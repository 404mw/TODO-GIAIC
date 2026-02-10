import { z } from 'zod';
import { ReminderTypeSchema, NotificationMethodSchema } from './common.schema';

/**
 * Reminder schema matching backend Reminder model.
 * Per data-model.md Entity 6 (FR-025)
 */
export const ReminderSchema = z.object({
  id: z.string().uuid(),
  task_id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Reminder details
  type: ReminderTypeSchema,
  offset_minutes: z.number().int().nullable(),
  method: NotificationMethodSchema.default('in_app'),

  // Scheduled time
  scheduled_at: z.string().datetime(),

  // Firing status
  fired: z.boolean().default(false),
  fired_at: z.string().datetime().nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Request schema for creating a reminder
 */
export const CreateReminderRequestSchema = ReminderSchema.pick({
  type: true,
  offset_minutes: true,
  method: true,
  scheduled_at: true,
}).partial({
  method: true,
});

/**
 * Request schema for updating a reminder
 */
export const UpdateReminderRequestSchema = ReminderSchema.pick({
  type: true,
  offset_minutes: true,
  method: true,
  scheduled_at: true,
}).partial();

// Reminder presets for common use cases
export const REMINDER_PRESETS = {
  FIVE_MIN_BEFORE: -5,
  FIFTEEN_MIN_BEFORE: -15,
  THIRTY_MIN_BEFORE: -30,
  ONE_HOUR_BEFORE: -60,
  ONE_DAY_BEFORE: -1440,
  AT_DUE_TIME: 0,
} as const;

export const REMINDER_PRESET_LABELS: Record<number, string> = {
  [REMINDER_PRESETS.FIVE_MIN_BEFORE]: '5 minutes before',
  [REMINDER_PRESETS.FIFTEEN_MIN_BEFORE]: '15 minutes before',
  [REMINDER_PRESETS.THIRTY_MIN_BEFORE]: '30 minutes before',
  [REMINDER_PRESETS.ONE_HOUR_BEFORE]: '1 hour before',
  [REMINDER_PRESETS.ONE_DAY_BEFORE]: '1 day before',
  [REMINDER_PRESETS.AT_DUE_TIME]: 'At due time',
};

// Type exports
export type Reminder = z.infer<typeof ReminderSchema>;
export type CreateReminderRequest = z.infer<typeof CreateReminderRequestSchema>;
export type UpdateReminderRequest = z.infer<typeof UpdateReminderRequestSchema>;
export type ReminderCreate = CreateReminderRequest;
