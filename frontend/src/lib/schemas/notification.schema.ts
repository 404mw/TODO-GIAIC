import { z } from 'zod';
import { DataResponseSchema, PaginatedResponseSchema } from './response.schema';

/**
 * Notification schema matching backend Notification model.
 * Per API.md FR-011 / FR-013 (T171)
 *
 * Fields align with backend API contract used by /notifications endpoints.
 */
export const NotificationSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Notification content (API.md contract)
  title: z.string(),
  message: z.string(),

  // Read status
  read: z.boolean().default(false),

  // Related task (nullable — notification may not be task-related)
  task_id: z.string().nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Notification response wrappers per API.md
 * Used by useNotifications (T092), /dashboard/notifications page (T128),
 * and mark-as-read hook (T129).
 */
export const NotificationResponseSchema = DataResponseSchema(NotificationSchema);
export const NotificationListResponseSchema = PaginatedResponseSchema(NotificationSchema);

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

// Type exports
export type Notification = z.infer<typeof NotificationSchema>;
export type PushSubscription = z.infer<typeof PushSubscriptionSchema>;
export type CreatePushSubscriptionRequest = z.infer<typeof CreatePushSubscriptionRequestSchema>;
