import { z } from 'zod';

/**
 * Pagination metadata schema
 * Used in paginated API responses per API.md specification
 */
export const PaginationMetaSchema = z.object({
  offset: z.number().int().min(0),
  limit: z.number().int().min(1).max(100),
  total: z.number().int().min(0),
  has_more: z.boolean(),
});

/**
 * Generic single-item response wrapper
 * API.md format: {"data": T}
 *
 * @example
 * // GET /api/v1/users/me
 * const userResponse: DataResponse<User> = {"data": {...}}
 */
export const DataResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    data: dataSchema,
  });

/**
 * Generic paginated response wrapper
 * API.md format: {"data": T[], "pagination": {...}}
 *
 * @example
 * // GET /api/v1/tasks
 * const tasksResponse: PaginatedResponse<Task> = {
 *   "data": [...],
 *   "pagination": {"offset": 0, "limit": 25, "total": 100, "has_more": true}
 * }
 */
export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    data: z.array(itemSchema),
    pagination: PaginationMetaSchema,
  });

// TypeScript type exports
export type PaginationMeta = z.infer<typeof PaginationMetaSchema>;

/**
 * TypeScript utility type for single-item responses
 */
export type DataResponse<T> = {
  data: T;
};

/**
 * TypeScript utility type for paginated responses
 */
export type PaginatedResponse<T> = {
  data: T[];
  pagination: PaginationMeta;
};
