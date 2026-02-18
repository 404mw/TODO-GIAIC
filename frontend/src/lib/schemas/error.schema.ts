import { z } from 'zod';

/**
 * Error codes from API.md specification
 * Maps to specific HTTP status codes and error conditions
 */
export enum ApiErrorCode {
  // 400 Bad Request
  VALIDATION_ERROR = 'VALIDATION_ERROR',

  // 401 Unauthorized
  UNAUTHORIZED = 'UNAUTHORIZED',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  INVALID_REFRESH_TOKEN = 'INVALID_REFRESH_TOKEN',

  // 402 Payment Required
  INSUFFICIENT_CREDITS = 'INSUFFICIENT_CREDITS',

  // 403 Forbidden
  FORBIDDEN = 'FORBIDDEN',
  TIER_REQUIRED = 'TIER_REQUIRED',

  // 404 Not Found
  NOT_FOUND = 'NOT_FOUND',
  TASK_NOT_FOUND = 'TASK_NOT_FOUND',

  // 409 Conflict
  CONFLICT = 'CONFLICT',
  LIMIT_EXCEEDED = 'LIMIT_EXCEEDED',
  ARCHIVED = 'ARCHIVED',

  // 429 Too Many Requests
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  AI_TASK_LIMIT_REACHED = 'AI_TASK_LIMIT_REACHED',

  // 503 Service Unavailable
  AI_SERVICE_UNAVAILABLE = 'AI_SERVICE_UNAVAILABLE',
  TRANSCRIPTION_SERVICE_UNAVAILABLE = 'TRANSCRIPTION_SERVICE_UNAVAILABLE',

  // Generic
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

/**
 * Field-level validation error detail
 * Used in VALIDATION_ERROR responses for field-specific errors
 */
export const ValidationErrorDetailSchema = z.object({
  field: z.string(),
  message: z.string(),
});

/**
 * API error schema matching API.md specification
 * Structure: {"code": "ERROR_CODE", "message": "...", "details": [...], "request_id": "req-uuid"}
 */
export const ApiErrorSchema = z.object({
  code: z.nativeEnum(ApiErrorCode),
  message: z.string(),
  details: z.array(ValidationErrorDetailSchema).optional(),
  request_id: z.string().optional(),
});

/**
 * Error response wrapper
 * API.md format: {"error": {...}}
 *
 * @example
 * // 400 Bad Request
 * {
 *   "error": {
 *     "code": "VALIDATION_ERROR",
 *     "message": "Invalid request data",
 *     "details": [{"field": "title", "message": "Required"}],
 *     "request_id": "req-uuid"
 *   }
 * }
 */
export const ErrorResponseSchema = z.object({
  error: ApiErrorSchema,
});

// TypeScript type exports
export type ValidationErrorDetail = z.infer<typeof ValidationErrorDetailSchema>;
export type ApiError = z.infer<typeof ApiErrorSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
