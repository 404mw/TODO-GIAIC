/**
 * TypeScript types for Perpetua Flow Backend API
 *
 * T383: Generated TypeScript types for frontend contract alignment
 *
 * These types are derived from the backend Pydantic schemas and OpenAPI spec.
 * Keep these in sync with:
 * - backend/src/schemas/*.py (Pydantic schemas)
 * - contracts/openapi.yaml (OpenAPI specification)
 *
 * Generation: Run `openapi-typescript` on the OpenAPI spec for automated updates.
 *
 * @see https://github.com/drwpow/openapi-typescript
 */

// =============================================================================
// ENUMS
// =============================================================================

/** Task priority levels */
export type TaskPriority = 'low' | 'medium' | 'high';

/** How a task was completed */
export type CompletedBy = 'user' | 'force' | 'subtasks';

/** Reminder type */
export type ReminderType = 'before' | 'after' | 'at';

/** Credit type for AI operations */
export type CreditType = 'kickstart' | 'daily' | 'subscription' | 'purchased';

/** Credit operation type */
export type CreditOperation = 'grant' | 'consume' | 'expire' | 'refund';

/** Subscription status */
export type SubscriptionStatus = 'none' | 'active' | 'grace_period' | 'cancelled' | 'expired';

/** User tier */
export type UserTier = 'free' | 'pro';

/** Notification type */
export type NotificationType = 'reminder' | 'achievement' | 'subscription' | 'system';

/** Subtask source */
export type SubtaskSource = 'user' | 'ai';

/** Note transcription status */
export type TranscriptionStatus = 'none' | 'pending' | 'completed' | 'failed';

/** Activity log action */
export type ActivityAction = 'created' | 'updated' | 'deleted' | 'completed' | 'recovered';

/** Activity log source */
export type ActivitySource = 'user' | 'ai' | 'system';

// =============================================================================
// AUTH TYPES
// =============================================================================

/** Request to exchange Google OAuth token */
export interface GoogleAuthRequest {
  id_token: string;
}

/** Request to refresh access token */
export interface RefreshRequest {
  refresh_token: string;
}

/** Auth response with tokens */
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;
  user: UserResponse;
}

/** Token refresh response */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;
}

/** JWKS response */
export interface JWKSResponse {
  keys: JWK[];
}

/** JSON Web Key */
export interface JWK {
  kty: string;
  kid: string;
  use?: string;
  alg?: string;
  n?: string;
  e?: string;
}

// =============================================================================
// USER TYPES
// =============================================================================

/** User response */
export interface UserResponse {
  id: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
  timezone: string;
  tier: UserTier;
  created_at: string;
  updated_at: string;
}

/** User update request */
export interface UserUpdateRequest {
  name?: string;
  timezone?: string;
}

// =============================================================================
// TASK TYPES
// =============================================================================

/** Task creation request */
export interface TaskCreateRequest {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  due_date?: string | null;
  estimated_duration?: number | null;
  template_id?: string | null;
}

/** Task update request (PATCH semantics) */
export interface TaskUpdateRequest {
  title?: string;
  description?: string | null;
  priority?: TaskPriority;
  due_date?: string | null;
  estimated_duration?: number | null;
  is_completed?: boolean;
  is_archived?: boolean;
  version: number;
}

/** Task response */
export interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  priority: TaskPriority;
  due_date: string | null;
  estimated_duration: number | null;
  is_completed: boolean;
  completed_at: string | null;
  completed_by: CompletedBy | null;
  is_archived: boolean;
  is_hidden: boolean;
  focus_time_seconds: number;
  ai_request_count: number;
  template_id: string | null;
  version: number;
  created_at: string;
  updated_at: string;
  subtasks?: SubtaskResponse[];
  reminders?: ReminderResponse[];
}

/** Task response with unlocked achievements (after completion) */
export interface TaskCompletionResponse extends TaskResponse {
  unlocked_achievements?: AchievementResponse[];
}

/** Task list response with pagination */
export interface TaskListResponse {
  data: TaskResponse[];
  pagination: PaginationMeta;
}

// =============================================================================
// SUBTASK TYPES
// =============================================================================

/** Subtask creation request */
export interface SubtaskCreateRequest {
  title: string;
}

/** Subtask update request */
export interface SubtaskUpdateRequest {
  title?: string;
  is_completed?: boolean;
}

/** Subtask response */
export interface SubtaskResponse {
  id: string;
  title: string;
  is_completed: boolean;
  order_index: number;
  source: SubtaskSource;
  task_id: string;
  created_at: string;
  updated_at: string;
}

/** Subtask reorder request */
export interface SubtaskReorderRequest {
  subtask_ids: string[];
}

// =============================================================================
// RECURRING TASK TEMPLATE TYPES
// =============================================================================

/** Template creation request */
export interface TemplateCreateRequest {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  estimated_duration?: number | null;
  rrule: string;
}

/** Template update request */
export interface TemplateUpdateRequest {
  title?: string;
  description?: string | null;
  priority?: TaskPriority;
  estimated_duration?: number | null;
  rrule?: string;
  is_active?: boolean;
}

/** Template response */
export interface TemplateResponse {
  id: string;
  title: string;
  description: string | null;
  priority: TaskPriority;
  estimated_duration: number | null;
  rrule: string;
  rrule_description: string;
  is_active: boolean;
  last_generated_at: string | null;
  next_due_at: string | null;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// NOTE TYPES
// =============================================================================

/** Note creation request */
export interface NoteCreateRequest {
  content: string;
  voice_url?: string | null;
  voice_duration_seconds?: number | null;
}

/** Note update request */
export interface NoteUpdateRequest {
  content?: string;
}

/** Note response */
export interface NoteResponse {
  id: string;
  content: string;
  voice_url: string | null;
  voice_duration_seconds: number | null;
  transcription_text: string | null;
  transcription_status: TranscriptionStatus;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

/** Note conversion response */
export interface NoteConversionResponse {
  task: TaskSuggestion;
  note_understanding: string;
  confidence: number;
}

// =============================================================================
// REMINDER TYPES
// =============================================================================

/** Reminder creation request */
export interface ReminderCreateRequest {
  type: ReminderType;
  offset_minutes?: number | null;
  scheduled_at?: string | null;
}

/** Reminder update request */
export interface ReminderUpdateRequest {
  type?: ReminderType;
  offset_minutes?: number | null;
  scheduled_at?: string | null;
}

/** Reminder response */
export interface ReminderResponse {
  id: string;
  type: ReminderType;
  offset_minutes: number | null;
  scheduled_at: string;
  is_fired: boolean;
  task_id: string;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// AI TYPES
// =============================================================================

/** AI chat request */
export interface ChatRequest {
  message: string;
  task_id: string;
  context?: string | null;
}

/** AI chat response (streamed via SSE) */
export interface ChatResponse {
  response_text: string;
  suggested_actions?: ActionSuggestion[];
  ai_request_warning?: boolean;
  credits_used: number;
  credits_remaining: number;
}

/** AI chat SSE event */
export interface ChatSSEEvent {
  type: 'content' | 'action' | 'done' | 'error';
  data: string | ActionSuggestion | ChatResponse;
}

/** AI action suggestion (requires user confirmation - FR-034) */
export interface ActionSuggestion {
  action_type: 'complete_task' | 'create_subtask' | 'update_task' | 'create_reminder';
  target_id: string | null;
  action_description: string;
  parameters: Record<string, unknown> | null;
  confidence: number;
}

/** Action confirmation request */
export interface ActionConfirmRequest {
  action_id: string;
  confirmed: boolean;
}

/** Subtask generation request */
export interface SubtaskGenerationRequest {
  task_id: string;
  count?: number;
}

/** Subtask suggestion from AI */
export interface SubtaskSuggestion {
  title: string;
  rationale?: string | null;
}

/** Subtask generation response */
export interface SubtaskGenerationResponse {
  subtasks: SubtaskSuggestion[];
  task_understanding: string;
  credits_used: number;
  credits_remaining: number;
}

/** Task suggestion from note conversion */
export interface TaskSuggestion {
  title: string;
  description: string | null;
  priority: TaskPriority;
  due_date: string | null;
  estimated_duration: number | null;
  subtasks: SubtaskSuggestion[];
}

/** Voice transcription request */
export interface TranscriptionRequest {
  audio: Blob | File;
  note_id?: string | null;
}

/** Voice transcription response */
export interface TranscriptionResponse {
  text: string;
  language: string;
  confidence: number;
  duration_seconds: number;
  credits_used: number;
  credits_remaining: number;
}

/** AI credits response */
export interface CreditsResponse {
  total: number;
  daily: number;
  subscription: number;
  purchased: number;
  kickstart: number;
  daily_expires_at: string | null;
}

// =============================================================================
// ACHIEVEMENT TYPES
// =============================================================================

/** Achievement definition */
export interface AchievementDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  threshold: number;
  perk: AchievementPerk | null;
}

/** Achievement perk */
export interface AchievementPerk {
  type: 'max_tasks' | 'max_notes' | 'max_subtasks' | 'credits';
  value: number;
}

/** User achievement state */
export interface AchievementResponse {
  id: string;
  name: string;
  description: string;
  is_unlocked: boolean;
  unlocked_at: string | null;
  progress: number;
  threshold: number;
  perk: AchievementPerk | null;
}

/** User stats response */
export interface UserStatsResponse {
  current_streak: number;
  longest_streak: number;
  total_tasks_completed: number;
  total_focus_completions: number;
  total_notes_converted: number;
}

/** Effective limits response */
export interface EffectiveLimitsResponse {
  max_tasks: number;
  max_notes: number;
  max_subtasks_per_task: number;
  base_limits: {
    max_tasks: number;
    max_notes: number;
    max_subtasks_per_task: number;
  };
  perk_bonuses: {
    max_tasks: number;
    max_notes: number;
    max_subtasks_per_task: number;
  };
}

// =============================================================================
// SUBSCRIPTION TYPES
// =============================================================================

/** Subscription status response */
export interface SubscriptionResponse {
  status: SubscriptionStatus;
  tier: UserTier;
  current_period_end: string | null;
  grace_period_end: string | null;
  cancel_at_period_end: boolean;
  monthly_credits_purchased: number;
  max_monthly_credits: number;
}

/** Checkout session request */
export interface CheckoutSessionRequest {
  plan: 'pro_monthly' | 'pro_yearly';
  success_url: string;
  cancel_url: string;
}

/** Checkout session response */
export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

// =============================================================================
// NOTIFICATION TYPES
// =============================================================================

/** Notification response */
export interface NotificationResponse {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  data: Record<string, unknown> | null;
  created_at: string;
}

/** Notification list response */
export interface NotificationListResponse {
  data: NotificationResponse[];
  pagination: PaginationMeta;
  unread_count: number;
}

/** Push subscription request */
export interface PushSubscriptionRequest {
  endpoint: string;
  p256dh_key: string;
  auth_key: string;
}

// =============================================================================
// RECOVERY TYPES
// =============================================================================

/** Tombstone (deleted task) response */
export interface TombstoneResponse {
  id: string;
  entity_type: 'task';
  entity_id: string;
  entity_title: string;
  deleted_at: string;
  expires_at: string;
}

/** Tombstone list response */
export interface TombstoneListResponse {
  data: TombstoneResponse[];
}

/** Recovery response */
export interface RecoveryResponse {
  task: TaskResponse;
  message: string;
}

// =============================================================================
// FOCUS TYPES
// =============================================================================

/** Focus session start request */
export interface FocusStartRequest {
  task_id: string;
}

/** Focus session end request */
export interface FocusEndRequest {
  task_id: string;
}

/** Focus session response */
export interface FocusSessionResponse {
  task_id: string;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number;
  is_active: boolean;
}

// =============================================================================
// ACTIVITY TYPES
// =============================================================================

/** Activity log entry */
export interface ActivityLogResponse {
  id: string;
  entity_type: string;
  entity_id: string;
  action: ActivityAction;
  source: ActivitySource;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

/** Activity log list response */
export interface ActivityLogListResponse {
  data: ActivityLogResponse[];
  pagination: PaginationMeta;
}

// =============================================================================
// COMMON TYPES
// =============================================================================

/** Pagination parameters for list requests */
export interface PaginationParams {
  offset?: number;
  limit?: number;
}

/** Pagination metadata in responses */
export interface PaginationMeta {
  offset: number;
  limit: number;
  total: number;
  has_more: boolean;
}

/** Standard error response */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/** Validation error response (422) */
export interface ValidationErrorResponse {
  detail: ValidationError[];
}

/** Individual validation error */
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

// =============================================================================
// API FUNCTION TYPES
// =============================================================================

/** Task list filters */
export interface TaskListFilters extends PaginationParams {
  is_completed?: boolean;
  is_archived?: boolean;
  priority?: TaskPriority;
  due_before?: string;
  due_after?: string;
  template_id?: string;
}

/** Note list filters */
export interface NoteListFilters extends PaginationParams {
  is_archived?: boolean;
}

/** Notification list filters */
export interface NotificationListFilters extends PaginationParams {
  is_read?: boolean;
  type?: NotificationType;
}

// =============================================================================
// WEBSOCKET TYPES (Voice Streaming)
// =============================================================================

/** Voice WebSocket message types */
export type VoiceWSMessageType =
  | 'transcript'
  | 'complete'
  | 'error';

/** Voice transcript message */
export interface VoiceTranscriptMessage {
  type: 'transcript';
  text: string;
  is_final: boolean;
}

/** Voice session complete message */
export interface VoiceCompleteMessage {
  type: 'complete';
  credits_used: number;
  duration_seconds: number;
  full_text: string;
}

/** Voice error message */
export interface VoiceErrorMessage {
  type: 'error';
  code: 'INSUFFICIENT_CREDITS' | 'MAX_DURATION_EXCEEDED' | 'TRANSCRIPTION_FAILED';
  message: string;
}

/** Voice WebSocket message union */
export type VoiceWSMessage =
  | VoiceTranscriptMessage
  | VoiceCompleteMessage
  | VoiceErrorMessage;

/** Voice control message from client */
export interface VoiceControlMessage {
  type: 'end_stream';
}
