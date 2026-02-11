import { z } from 'zod';
import { DataResponseSchema } from './response.schema';
import { UserTierSchema } from './common.schema';

/**
 * AI Chat request schema
 * API.md: POST /api/v1/ai/chat
 * Cost: 1 credit per message
 * Requires Idempotency-Key header
 */
export const AIChatRequestSchema = z.object({
  message: z.string().min(1),
  context: z
    .object({
      include_tasks: z.boolean().optional(),
      task_limit: z.number().int().min(1).max(50).optional(),
    })
    .optional(),
});

/**
 * AI Suggested Action schema
 * Represents an action that the AI recommends the user to take
 */
export const AISuggestedActionSchema = z.object({
  type: z.enum(['complete_task', 'create_subtasks', 'update_task']),
  task_id: z.string().uuid().optional(),
  description: z.string(),
  data: z.record(z.string(), z.unknown()),
});

/**
 * AI Chat response schema
 * API.md: POST /api/v1/ai/chat returns {"data": {...}}
 */
export const AIChatResponseSchema = DataResponseSchema(
  z.object({
    response: z.string(),
    suggested_actions: z.array(AISuggestedActionSchema),
    credits_used: z.number().int().min(0),
    credits_remaining: z.number().int().min(0),
    ai_request_warning: z.boolean(),
  })
);

/**
 * AI Generate Subtasks request schema
 * API.md: POST /api/v1/ai/generate-subtasks
 * Cost: 1 credit per generation
 * Tier limits: Free (4 subtasks max), Pro (10 subtasks max)
 */
export const AIGenerateSubtasksRequestSchema = z.object({
  task_id: z.string().uuid(),
});

/**
 * Suggested subtask schema (from AI generation)
 */
export const AISuggestedSubtaskSchema = z.object({
  title: z.string().min(1).max(200),
});

/**
 * AI Generate Subtasks response schema
 * API.md: POST /api/v1/ai/generate-subtasks returns {"data": {...}}
 */
export const AIGenerateSubtasksResponseSchema = DataResponseSchema(
  z.object({
    suggested_subtasks: z.array(AISuggestedSubtaskSchema),
    credits_used: z.number().int().min(0),
    credits_remaining: z.number().int().min(0),
  })
);

/**
 * AI Transcribe Voice request schema
 * API.md: POST /api/v1/ai/transcribe (Pro only)
 * Cost: 5 credits per minute (rounded up)
 * Max duration: 300 seconds (5 minutes)
 */
export const AITranscribeRequestSchema = z.object({
  audio_url: z.string().url(),
  duration_seconds: z.number().int().min(1).max(300),
});

/**
 * AI Transcribe Voice response schema
 * API.md: POST /api/v1/ai/transcribe returns {"data": {...}}
 */
export const AITranscribeResponseSchema = DataResponseSchema(
  z.object({
    transcription: z.string(),
    language: z.string(),
    confidence: z.number().min(0).max(1),
    credits_used: z.number().int().min(0),
    credits_remaining: z.number().int().min(0),
  })
);

/**
 * AI Confirm Action request schema
 * API.md: POST /api/v1/ai/confirm-action
 * Executes AI-suggested action after user confirmation
 */
export const AIConfirmActionRequestSchema = z.object({
  action_type: z.enum(['complete_task', 'create_subtasks', 'update_task']),
  action_data: z.record(z.string(), z.unknown()),
});

/**
 * AI Confirm Action response schema
 * API.md: POST /api/v1/ai/confirm-action returns {"data": {...}}
 * Response structure varies by action_type
 */
export const AIConfirmActionResponseSchema = DataResponseSchema(z.record(z.string(), z.unknown()));

/**
 * Credit balance breakdown schema
 */
export const CreditBalanceBreakdownSchema = z.object({
  daily_free: z.number().int().min(0),
  subscription: z.number().int().min(0),
  purchased: z.number().int().min(0),
  total: z.number().int().min(0),
});

/**
 * AI Credits Balance schema
 * API.md: GET /api/v1/ai/credits returns {"data": {...}}
 */
export const AICreditsBalanceSchema = DataResponseSchema(
  z.object({
    balance: CreditBalanceBreakdownSchema,
    daily_reset_at: z.string().datetime(),
    tier: UserTierSchema,
  })
);

// Type exports
export type AIChatRequest = z.infer<typeof AIChatRequestSchema>;
export type AISuggestedAction = z.infer<typeof AISuggestedActionSchema>;
export type AIChatResponse = z.infer<typeof AIChatResponseSchema>;
export type AIGenerateSubtasksRequest = z.infer<typeof AIGenerateSubtasksRequestSchema>;
export type AISuggestedSubtask = z.infer<typeof AISuggestedSubtaskSchema>;
export type AIGenerateSubtasksResponse = z.infer<typeof AIGenerateSubtasksResponseSchema>;
export type AITranscribeRequest = z.infer<typeof AITranscribeRequestSchema>;
export type AITranscribeResponse = z.infer<typeof AITranscribeResponseSchema>;
export type AIConfirmActionRequest = z.infer<typeof AIConfirmActionRequestSchema>;
export type AIConfirmActionResponse = z.infer<typeof AIConfirmActionResponseSchema>;
export type CreditBalanceBreakdown = z.infer<typeof CreditBalanceBreakdownSchema>;
export type AICreditsBalance = z.infer<typeof AICreditsBalanceSchema>;
