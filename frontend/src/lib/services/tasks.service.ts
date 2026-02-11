import { apiClient } from '@/lib/api/client';
import {
  TaskListResponseSchema,
  TaskDetailResponseSchema,
  TaskResponseSchema,
  TaskForceCompleteResponseSchema,
  TaskDeleteResponseSchema,
  CreateTaskRequestSchema,
  UpdateTaskRequestSchema,
  ForceCompleteTaskRequestSchema,
  type Task,
  type TaskListResponse,
  type TaskDetailResponse,
  type TaskResponse,
  type TaskForceCompleteResponse,
  type TaskDeleteResponse,
  type CreateTaskRequest,
  type UpdateTaskRequest,
  type ForceCompleteTaskRequest,
} from '@/lib/schemas/task.schema';

/**
 * Task list query filters
 * API.md: GET /api/v1/tasks query parameters
 */
export interface TaskListFilters {
  offset?: number;          // Pagination offset (default: 0)
  limit?: number;           // Items per page (max 100, default: 25)
  completed?: boolean;      // Filter by completion status
  priority?: 'low' | 'medium' | 'high';  // Filter by priority
  hidden?: boolean;         // Include hidden tasks (default: false)
  due_before?: string;      // Tasks due before this date (ISO 8601)
  due_after?: string;       // Tasks due after this date (ISO 8601)
}

/**
 * Tasks Service
 * Handles task CRUD operations, force completion, and deletion
 * API.md: Tasks section
 */
export const tasksService = {
  /**
   * Get paginated list of tasks with optional filters
   * API.md: GET /api/v1/tasks
   *
   * @param filters - Optional query parameters for filtering and pagination
   * @returns Paginated list of tasks with subtask counts
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code VALIDATION_ERROR if invalid filter parameters
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * // Get all active high-priority tasks
   * const response = await tasksService.listTasks({
   *   completed: false,
   *   priority: 'high',
   *   limit: 50
   * });
   * const tasks = response.data;
   * const { offset, limit, total, has_more } = response.pagination;
   * ```
   */
  async listTasks(filters?: TaskListFilters): Promise<TaskListResponse> {
    // Build query string from filters
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }

    const endpoint = `/tasks${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get<TaskListResponse>(
      endpoint,
      TaskListResponseSchema
    );

    return response;
  },

  /**
   * Get detailed task information including subtasks and reminders
   * API.md: GET /api/v1/tasks/{task_id}
   *
   * @param taskId - UUID of the task to retrieve
   * @returns Task detail with nested subtasks and reminders
   * @throws ApiError with code NOT_FOUND if task doesn't exist
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await tasksService.getTask('550e8400-e29b-41d4-a716-446655440001');
   * const task = response.data;
   * console.log(task.subtasks, task.reminders);
   * ```
   */
  async getTask(taskId: string): Promise<TaskDetailResponse> {
    const response = await apiClient.get<TaskDetailResponse>(
      `/tasks/${taskId}`,
      TaskDetailResponseSchema
    );

    return response;
  },

  /**
   * Create a new task with idempotency support
   * API.md: POST /api/v1/tasks
   *
   * @param data - Task creation request (title required, others optional)
   * @returns Created task wrapped in DataResponse
   * @throws ApiError with code VALIDATION_ERROR if invalid data (title 1-500 chars, description max 5000)
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await tasksService.createTask({
   *   title: 'Write documentation',
   *   description: 'Create API documentation for frontend team',
   *   priority: 'medium',
   *   due_date: '2026-02-20T17:00:00.000Z',
   *   estimated_duration: 180
   * });
   * const newTask = response.data;
   * ```
   */
  async createTask(data: CreateTaskRequest): Promise<TaskResponse> {
    // Validate request schema
    CreateTaskRequestSchema.parse(data);

    const response = await apiClient.post<TaskResponse>(
      '/tasks',
      data,
      TaskResponseSchema
    );

    return response;
  },

  /**
   * Update task with optimistic locking (version check)
   * API.md: PATCH /api/v1/tasks/{task_id}
   *
   * @param taskId - UUID of the task to update
   * @param data - Task update request (version required for optimistic locking)
   * @returns Updated task wrapped in DataResponse (version incremented)
   * @throws ApiError with code NOT_FOUND if task doesn't exist
   * @throws ApiError with code CONFLICT if version mismatch (concurrent update detected)
   * @throws ApiError with code VALIDATION_ERROR if invalid data
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await tasksService.updateTask('550e8400-e29b-41d4-a716-446655440001', {
   *   title: 'Write comprehensive documentation',
   *   priority: 'high',
   *   version: 1  // Required for optimistic locking
   * });
   * const updatedTask = response.data;
   * console.log(updatedTask.version); // Incremented to 2
   * ```
   */
  async updateTask(taskId: string, data: UpdateTaskRequest): Promise<TaskResponse> {
    // Validate request schema (ensures version is present)
    UpdateTaskRequestSchema.parse(data);

    const response = await apiClient.patch<TaskResponse>(
      `/tasks/${taskId}`,
      data,
      TaskResponseSchema
    );

    return response;
  },

  /**
   * Force complete task and all incomplete subtasks with achievement tracking
   * API.md: POST /api/v1/tasks/{task_id}/force-complete
   *
   * @param taskId - UUID of the task to force complete
   * @param version - Current version for optimistic locking
   * @returns Task, unlocked achievements, and current streak
   * @throws ApiError with code NOT_FOUND if task doesn't exist
   * @throws ApiError with code CONFLICT if version mismatch
   * @throws ApiError with code ARCHIVED if task is archived
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await tasksService.forceCompleteTask(
   *   '550e8400-e29b-41d4-a716-446655440001',
   *   1
   * );
   * const { task, unlocked_achievements, streak } = response.data;
   * console.log(`Task completed! Current streak: ${streak} days`);
   * unlocked_achievements.forEach(a => console.log(`🏆 ${a.name}`));
   * ```
   */
  async forceCompleteTask(taskId: string, version: number): Promise<TaskForceCompleteResponse> {
    const data: ForceCompleteTaskRequest = { version };

    // Validate request schema
    ForceCompleteTaskRequestSchema.parse(data);

    const response = await apiClient.post<TaskForceCompleteResponse>(
      `/tasks/${taskId}/force-complete`,
      data,
      TaskForceCompleteResponseSchema
    );

    return response;
  },

  /**
   * Hard delete task and create recovery tombstone
   * API.md: DELETE /api/v1/tasks/{task_id}
   *
   * @param taskId - UUID of the task to delete
   * @returns Tombstone ID and recovery expiration date (7 days)
   * @throws ApiError with code NOT_FOUND if task doesn't exist
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   * @throws ApiError with code RATE_LIMIT_EXCEEDED if too many requests (100/minute)
   *
   * @example
   * ```ts
   * const response = await tasksService.deleteTask('550e8400-e29b-41d4-a716-446655440001');
   * const { tombstone_id, recoverable_until } = response.data;
   * console.log(`Task deleted. Recoverable until ${recoverable_until}`);
   * ```
   *
   * @note Tasks are recoverable for 7 days after deletion via the Recovery API
   */
  async deleteTask(taskId: string): Promise<TaskDeleteResponse> {
    const response = await apiClient.delete<TaskDeleteResponse>(
      `/tasks/${taskId}`,
      TaskDeleteResponseSchema
    );

    return response;
  },
};
