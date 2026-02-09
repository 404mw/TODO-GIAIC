import { z } from 'zod'

/**
 * Credit Source Types
 * Defines where credits can come from
 */
export const CreditSourceSchema = z.enum([
  'signup',
  'subscription',
  'purchase',
  'bonus',
  'refund',
])

/**
 * Credit Transaction Schema
 * Represents a single credit transaction (addition or deduction)
 */
export const CreditTransactionSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  amount: z.number(),
  source: CreditSourceSchema,
  description: z.string(),
  created_at: z.string().datetime(),
})

/**
 * Credit Balance Schema
 * Represents the user's current credit balance breakdown
 */
export const CreditBalanceSchema = z.object({
  total_credits: z.number(),
  subscription_credits: z.number(),
  purchased_credits: z.number(),
  bonus_credits: z.number(),
})

/**
 * Credit Purchase Package Schema
 * Represents a purchasable credit package
 */
export const CreditPackageSchema = z.object({
  credits: z.number(),
  price: z.number(),
  discount: z.number().optional(),
})

// Type exports
export type CreditSource = z.infer<typeof CreditSourceSchema>
export type CreditTransaction = z.infer<typeof CreditTransactionSchema>
export type CreditBalance = z.infer<typeof CreditBalanceSchema>
export type CreditPackage = z.infer<typeof CreditPackageSchema>
