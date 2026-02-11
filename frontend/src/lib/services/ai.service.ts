import { apiClient } from '@/lib/api/client';
import {
  AIChatRequestSchema,
  AIChatResponseSchema,
  AIGenerateSubtasksRequestSchema,
  AIGenerateSubtasksResponseSchema,
  AITranscribeRequestSchema,
  AITranscribeResponseSchema,
  AIConfirmActionRequestSchema,
  AIConfirmActionResponseSchema,
  AICreditsBalanceSchema,
  type AIChatRequest,
  type AIChatResponse,
  type AIGenerateSubtasksRequest,
  type AIGenerateSubtasksResponse,
  type AITranscribeRequest,
  type AITranscribeResponse,
  type AIConfirmActionRequest,
  type AIConfirmActionResponse,
  type AICreditsBalance,
} from '@/lib/schemas/ai.schema';

/**
 * AI Service
 * Handles AI-powered features including chat, subtask generation, voice transcription, and action confirmation
 * API.md: AI section
 *
 * @note All AI endpoints require Idempotency-Key header (automatically added by apiClient)
 * @note All AI operations consume credits - check balance before calling
 */
export const aiService = {
  /**
   * Send message to AI assistant with context awareness
   * API.md: POST /api/v1/ai/chat
   *
   * @param message - User message to send to AI
   * @param context - Optional context (include tasks, task limit)
   * @returns AI response with suggested actions and credit info
   * @throws ApiError with code INSUFFICIENT_CREDITS if user has no credits
   * @throws ApiError with code AI_SERVICE_UNAVAILABLE if AI service is down
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (20/minute)
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await aiService.chat(
   *   'What tasks should I focus on today?',
   *   { include_tasks: true, task_limit: 10 }
   * );
   * const { response: aiResponse, suggested_actions, credits_used, credits_remaining } = response.data;
   * console.log(aiResponse);
   * suggested_actions.forEach(action => {
   *   console.log(`Suggested: ${action.description}`);
   * });
   * ```
   *
   * @note Cost: 1 credit per message
   * @note Requires Idempotency-Key header (auto-added)
   */
  async chat(message: string, context?: { include_tasks?: boolean; task_limit?: number }): Promise<AIChatResponse> {
    const request: AIChatRequest = { message, context };

    // Validate request schema
    AIChatRequestSchema.parse(request);

    const response = await apiClient.post<AIChatResponse>(
      '/ai/chat',
      request,
      AIChatResponseSchema
    );

    return response;
  },

  /**
   * Stream AI chat response via Server-Sent Events (SSE)
   * API.md: POST /api/v1/ai/chat/stream
   *
   * @param message - User message to send to AI
   * @param context - Optional context (include tasks, task limit)
   * @param onChunk - Callback for each streamed text chunk
   * @returns Promise that resolves when stream completes
   * @throws ApiError with code INSUFFICIENT_CREDITS if user has no credits
   * @throws ApiError with code AI_SERVICE_UNAVAILABLE if AI service is down
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (20/minute)
   *
   * @example
   * ```ts
   * await aiService.chatStream(
   *   'Explain this task to me',
   *   { include_tasks: true },
   *   (chunk) => {
   *     console.log(chunk.text); // Display streaming text
   *   }
   * );
   * console.log('Stream completed');
   * ```
   *
   * @note Cost: 1 credit per message
   * @note Requires Idempotency-Key header (auto-added)
   * @note This method uses EventSource for SSE streaming
   */
  async chatStream(
    message: string,
    context?: { include_tasks?: boolean; task_limit?: number },
    onChunk?: (chunk: { text: string }) => void
  ): Promise<void> {
    const request: AIChatRequest = { message, context };

    // Validate request schema
    AIChatRequestSchema.parse(request);

    // Note: SSE implementation requires EventSource, which is not part of apiClient
    // This is a placeholder for future implementation with proper SSE handling
    throw new Error('SSE streaming not yet implemented - use chat() for non-streaming');
  },

  /**
   * Generate AI subtask suggestions for a task
   * API.md: POST /api/v1/ai/generate-subtasks
   *
   * @param taskId - UUID of the task to generate subtasks for
   * @returns Suggested subtasks with credit info
   * @throws ApiError with code TASK_NOT_FOUND if task doesn't exist
   * @throws ApiError with code INSUFFICIENT_CREDITS if user has no credits
   * @throws ApiError with code AI_SERVICE_UNAVAILABLE if AI service is down
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (20/minute)
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await aiService.generateSubtasks('550e8400-e29b-41d4-a716-446655440001');
   * const { suggested_subtasks, credits_used, credits_remaining } = response.data;
   * suggested_subtasks.forEach(subtask => {
   *   console.log(`- ${subtask.title}`);
   * });
   * ```
   *
   * @note Cost: 1 credit per generation
   * @note Tier limits: Free (4 subtasks max), Pro (10 subtasks max)
   * @note Requires Idempotency-Key header (auto-added)
   */
  async generateSubtasks(taskId: string): Promise<AIGenerateSubtasksResponse> {
    const request: AIGenerateSubtasksRequest = { task_id: taskId };

    // Validate request schema
    AIGenerateSubtasksRequestSchema.parse(request);

    const response = await apiClient.post<AIGenerateSubtasksResponse>(
      '/ai/generate-subtasks',
      request,
      AIGenerateSubtasksResponseSchema
    );

    return response;
  },

  /**
   * Transcribe voice audio using Deepgram NOVA2 (Pro only)
   * API.md: POST /api/v1/ai/transcribe
   *
   * @param audioUrl - URL to audio file (webm, mp3, wav, etc.)
   * @param durationSeconds - Audio duration in seconds (max 300 seconds / 5 minutes)
   * @returns Transcription text, language, confidence, and credit info
   * @throws ApiError with code TIER_REQUIRED if user is not Pro
   * @throws ApiError with code AUDIO_DURATION_EXCEEDED if audio exceeds 300 seconds
   * @throws ApiError with code INSUFFICIENT_CREDITS if user has insufficient credits
   * @throws ApiError with code TRANSCRIPTION_SERVICE_UNAVAILABLE if service is down
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (20/minute)
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await aiService.transcribeVoice(
   *   'https://storage.example.com/audio/recording.webm',
   *   45
   * );
   * const { transcription, language, confidence, credits_used } = response.data;
   * console.log(`[${language}] ${transcription} (${confidence * 100}% confident)`);
   * ```
   *
   * @note Cost: 5 credits per minute (rounded up)
   * @note Credit calculation: 45s → 1 min → 5 credits, 90s → 2 min → 10 credits
   * @note Pro subscription required
   * @note Requires Idempotency-Key header (auto-added)
   */
  async transcribeVoice(audioUrl: string, durationSeconds: number): Promise<AITranscribeResponse> {
    const request: AITranscribeRequest = {
      audio_url: audioUrl,
      duration_seconds: durationSeconds,
    };

    // Validate request schema
    AITranscribeRequestSchema.parse(request);

    const response = await apiClient.post<AITranscribeResponse>(
      '/ai/transcribe',
      request,
      AITranscribeResponseSchema
    );

    return response;
  },

  /**
   * Execute AI-suggested action after user confirmation
   * API.md: POST /api/v1/ai/confirm-action
   *
   * @param actionType - Type of action (complete_task, create_subtasks, update_task)
   * @param actionData - Action-specific data (e.g., task_id, subtasks array)
   * @returns Action result (structure varies by action_type)
   * @throws ApiError with code VALIDATION_ERROR if invalid action data
   * @throws ApiError with code NOT_FOUND if referenced entity doesn't exist
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (20/minute)
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await aiService.confirmAction(
   *   'create_subtasks',
   *   {
   *     task_id: '550e8400-e29b-41d4-a716-446655440001',
   *     subtasks: [
   *       { title: 'Research market trends' },
   *       { title: 'Draft timeline' }
   *     ]
   *   }
   * );
   * const { subtasks } = response.data;
   * subtasks.forEach(subtask => console.log(`Created: ${subtask.title}`));
   * ```
   *
   * @note Supported actions: complete_task, create_subtasks, update_task
   * @note Requires Idempotency-Key header (auto-added)
   */
  async confirmAction(
    actionType: 'complete_task' | 'create_subtasks' | 'update_task',
    actionData: Record<string, unknown>
  ): Promise<AIConfirmActionResponse> {
    const request: AIConfirmActionRequest = {
      action_type: actionType,
      action_data: actionData,
    };

    // Validate request schema
    AIConfirmActionRequestSchema.parse(request);

    const response = await apiClient.post<AIConfirmActionResponse>(
      '/ai/confirm-action',
      request,
      AIConfirmActionResponseSchema
    );

    return response;
  },

  /**
   * Get AI credit balance breakdown
   * API.md: GET /api/v1/ai/credits
   *
   * @returns Credit balance breakdown, daily reset time, and user tier
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await aiService.getCredits();
   * const { balance, daily_reset_at, tier } = response.data;
   * console.log(`Total credits: ${balance.total}`);
   * console.log(`Daily free: ${balance.daily_free}`);
   * console.log(`Subscription: ${balance.subscription}`);
   * console.log(`Purchased: ${balance.purchased}`);
   * console.log(`Tier: ${tier}`);
   * console.log(`Daily reset: ${daily_reset_at}`);
   * ```
   *
   * @note Credit types:
   * - daily_free: Free daily credits (expire at UTC midnight)
   * - subscription: Pro subscription credits
   * - purchased: One-time purchased credits
   */
  async getCredits(): Promise<AICreditsBalance> {
    const response = await apiClient.get<AICreditsBalance>(
      '/ai/credits',
      AICreditsBalanceSchema
    );

    return response;
  },
};
