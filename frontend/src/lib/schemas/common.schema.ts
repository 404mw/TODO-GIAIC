import { z } from 'zod';

// ============================================================================
// User & Authentication Enums
// ============================================================================

export const UserTierSchema = z.enum(['free', 'pro']);

// ============================================================================
// Task Enums
// ============================================================================

export const PrioritySchema = z.enum(['low', 'medium', 'high']);
export const CompletedBySchema = z.enum(['manual', 'auto', 'force']);

// ============================================================================
// Subtask Enums
// ============================================================================

export const SubtaskSourceSchema = z.enum(['user', 'ai']);

// ============================================================================
// Note Enums
// ============================================================================

export const TranscriptionStatusSchema = z.enum(['pending', 'completed', 'failed']);

// ============================================================================
// Reminder Enums
// ============================================================================

export const ReminderTypeSchema = z.enum(['before', 'after', 'absolute']);
export const NotificationMethodSchema = z.enum(['push', 'in_app']);

// ============================================================================
// Achievement Enums
// ============================================================================

export const AchievementCategorySchema = z.enum(['tasks', 'streaks', 'focus', 'notes']);
export const PerkTypeSchema = z.enum(['max_tasks', 'max_notes', 'daily_credits']);

// ============================================================================
// Credit Enums
// ============================================================================

export const CreditTypeSchema = z.enum(['kickstart', 'daily', 'subscription', 'purchased']);
export const CreditOperationSchema = z.enum(['grant', 'consume', 'expire', 'carryover']);

// ============================================================================
// Subscription Enums
// ============================================================================

export const SubscriptionStatusSchema = z.enum([
  'active',
  'past_due',
  'grace',
  'cancelled',
  'expired',
]);

// ============================================================================
// Activity Log Enums
// ============================================================================

export const EntityTypeSchema = z.enum([
  'task',
  'subtask',
  'note',
  'reminder',
  'subscription',
  'achievement',
  'ai_chat',
]);

export const ActivitySourceSchema = z.enum(['user', 'ai', 'system']);

// ============================================================================
// Notification Enums
// ============================================================================

export const NotificationTypeSchema = z.enum([
  'reminder',
  'achievement',
  'subscription',
  'system',
]);

// ============================================================================
// Job Queue Enums
// ============================================================================

export const JobStatusSchema = z.enum(['pending', 'processing', 'completed', 'failed', 'dead']);

export const JobTypeSchema = z.enum([
  'reminder_fire',
  'streak_calculate',
  'credit_expire',
  'subscription_check',
  'recurring_task_generate',
]);

// ============================================================================
// Tombstone Enums
// ============================================================================

export const TombstoneEntityTypeSchema = z.enum(['task', 'note']);

// ============================================================================
// Type Exports
// ============================================================================

export type UserTier = z.infer<typeof UserTierSchema>;
export type Priority = z.infer<typeof PrioritySchema>;
export type CompletedBy = z.infer<typeof CompletedBySchema>;
export type SubtaskSource = z.infer<typeof SubtaskSourceSchema>;
export type TranscriptionStatus = z.infer<typeof TranscriptionStatusSchema>;
export type ReminderType = z.infer<typeof ReminderTypeSchema>;
export type NotificationMethod = z.infer<typeof NotificationMethodSchema>;
export type AchievementCategory = z.infer<typeof AchievementCategorySchema>;
export type PerkType = z.infer<typeof PerkTypeSchema>;
export type CreditType = z.infer<typeof CreditTypeSchema>;
export type CreditOperation = z.infer<typeof CreditOperationSchema>;
export type SubscriptionStatus = z.infer<typeof SubscriptionStatusSchema>;
export type EntityType = z.infer<typeof EntityTypeSchema>;
export type ActivitySource = z.infer<typeof ActivitySourceSchema>;
export type NotificationType = z.infer<typeof NotificationTypeSchema>;
export type JobStatus = z.infer<typeof JobStatusSchema>;
export type JobType = z.infer<typeof JobTypeSchema>;
export type TombstoneEntityType = z.infer<typeof TombstoneEntityTypeSchema>;
