import { z } from 'zod';
import { CreditTypeSchema, CreditOperationSchema } from './common.schema';

/**
 * AI Credit Ledger schema matching backend AICreditLedger model.
 * Per data-model.md Entity 9 (FR-042)
 */
export const AICreditLedgerSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Credit details
  credit_type: CreditTypeSchema,
  amount: z.number().int(), // Positive = credit, negative = debit
  balance_after: z.number().int().min(0),
  operation: CreditOperationSchema,
  operation_ref: z.string().nullable(),

  // Consumption tracking
  consumed: z.number().int().min(0).default(0),

  // Expiration (for daily credits)
  expires_at: z.string().datetime().nullable(),
  expired: z.boolean().default(false),

  // Reference to source (for expiration entries)
  source_id: z.string().uuid().nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Credit Balance summary schema
 */
export const CreditBalanceSchema = z.object({
  kickstart: z.number().int().min(0).default(0),
  daily: z.number().int().min(0).default(0),
  subscription: z.number().int().min(0).default(0),
  purchased: z.number().int().min(0).default(0),
  total: z.number().int().min(0).default(0),
});

/**
 * Credit consumption costs
 */
export const CreditCostSchema = z.object({
  ai_chat: z.number().int().default(1),
  subtask_generation: z.number().int().default(1),
  note_conversion: z.number().int().default(1),
  voice_per_minute: z.number().int().default(5),
});

// Type exports
export type AICreditLedger = z.infer<typeof AICreditLedgerSchema>;
export type CreditBalance = z.infer<typeof CreditBalanceSchema>;
export type CreditCost = z.infer<typeof CreditCostSchema>;
