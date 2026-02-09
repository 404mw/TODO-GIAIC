import { z } from 'zod';
import { NotificationTypeSchema } from './common.schema';

/**
 * Notification schema matching backend Notification model.
 * Per data-model.md Entity 13
 */
export const NotificationSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Notification content
  type: NotificationTypeSchema,
  title: z.string().max(100),
  body: z.string().max(500),
  action_url: z.string().nullable(),

  // Read status (FR-057)
  read: z.boolean().default(false),
  read_at: z.string().datetime().nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Push Subscription schema matching backend PushSubscription model.
 * Per FR-028a
 */
export const PushSubscriptionSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // WebPush fields
  endpoint: z.string(),
  p256dh_key: z.string(),
  auth_key: z.string(),

  // Status
  active: z.boolean().default(true),

  // Timestamps
  created_at: z.string().datetime(),
  last_used_at: z.string().datetime().nullable(),
});

/**
 * Request schema for creating a push subscription
 */
export const CreatePushSubscriptionRequestSchema = PushSubscriptionSchema.pick({
  endpoint: true,
  p256dh_key: true,
  auth_key: true,
});

/**
 * Request schema for marking notification as read
 */
export const MarkNotificationReadRequestSchema = z.object({
  read: z.boolean(),
});

// Type exports
export type Notification = z.infer<typeof NotificationSchema>;
export type PushSubscription = z.infer<typeof PushSubscriptionSchema>;
export type CreatePushSubscriptionRequest = z.infer<typeof CreatePushSubscriptionRequestSchema>;
export type MarkNotificationReadRequest = z.infer<typeof MarkNotificationReadRequestSchema>;
