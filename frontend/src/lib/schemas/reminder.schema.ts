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

// Type exports
export type Reminder = z.infer<typeof ReminderSchema>;
export type CreateReminderRequest = z.infer<typeof CreateReminderRequestSchema>;
export type UpdateReminderRequest = z.infer<typeof UpdateReminderRequestSchema>;
