import { z } from 'zod';
import { SubscriptionStatusSchema, UserTierSchema } from './common.schema';

/**
 * Subscription schema matching backend Subscription model.
 * Per data-model.md Entity 10
 */
export const SubscriptionSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Checkout.com integration
  checkout_subscription_id: z.string(),

  // Status
  status: SubscriptionStatusSchema,

  // Billing period
  current_period_start: z.string().datetime(),
  current_period_end: z.string().datetime(),

  // Grace period (FR-049)
  grace_period_end: z.string().datetime().nullable(),

  // Payment tracking
  failed_payment_count: z.number().int().min(0).default(0),
  retry_count: z.number().int().min(0).default(0),
  last_retry_at: z.string().datetime().nullable(),
  last_payment_at: z.string().datetime().nullable(),
  grace_warning_sent: z.boolean().default(false),

  // Cancellation
  cancelled_at: z.string().datetime().nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Subscription Features schema matching backend.
 * Features available with the subscription.
 */
export const SubscriptionFeaturesSchema = z.object({
  max_subtasks: z.number().int().min(1),
  max_description_length: z.number().int().min(1),
  voice_notes: z.boolean(),
  monthly_credits: z.number().int().min(0),
});

/**
 * Subscription Response schema matching backend.
 * Per api-specification.md Section 10.1
 */
export const SubscriptionResponseSchema = z.object({
  tier: UserTierSchema,
  status: SubscriptionStatusSchema.nullable(),
  current_period_end: z.string().datetime().nullable(),
  cancel_at_period_end: z.boolean().default(false),
  features: SubscriptionFeaturesSchema,
});

/**
 * Checkout Session Response schema matching backend.
 * Per api-specification.md Section 10.2
 */
export const CheckoutSessionResponseSchema = z.object({
  checkout_url: z.string(),
  session_id: z.string(),
});

/**
 * Cancel Subscription Response schema matching backend.
 * Per api-specification.md Section 10.3
 */
export const CancelSubscriptionResponseSchema = z.object({
  status: SubscriptionStatusSchema,
  access_until: z.string().datetime(),
});

/**
 * Purchase Credits Request schema matching backend.
 * Per FR-051
 */
export const PurchaseCreditsRequestSchema = z.object({
  amount: z.number().int().min(1).max(500),
});

/**
 * Purchase Credits Response schema matching backend.
 */
export const PurchaseCreditsResponseSchema = z.object({
  credits_added: z.number().int().min(1),
  total_credits: z.number().int().min(0),
  monthly_purchased: z.number().int().min(0),
  monthly_remaining: z.number().int().min(0),
});

// Type exports
export type Subscription = z.infer<typeof SubscriptionSchema>;
export type SubscriptionFeatures = z.infer<typeof SubscriptionFeaturesSchema>;
export type SubscriptionResponse = z.infer<typeof SubscriptionResponseSchema>;
export type CheckoutSessionResponse = z.infer<typeof CheckoutSessionResponseSchema>;
export type CancelSubscriptionResponse = z.infer<typeof CancelSubscriptionResponseSchema>;
export type PurchaseCreditsRequest = z.infer<typeof PurchaseCreditsRequestSchema>;
export type PurchaseCreditsResponse = z.infer<typeof PurchaseCreditsResponseSchema>;
