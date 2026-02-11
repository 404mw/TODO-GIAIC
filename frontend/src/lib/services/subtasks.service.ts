import { apiClient } from '@/lib/api/client';
import { DataResponseSchema } from '@/lib/schemas/response.schema';
import {
  SubtaskSchema,
  CreateSubtaskRequestSchema,
  UpdateSubtaskRequestSchema,
  type Subtask,
  type CreateSubtaskRequest,
  type UpdateSubtaskRequest,
} from '@/lib/schemas/subtask.schema';

// Response schemas for subtasks (following DataResponse pattern)
const SubtaskResponseSchema = DataResponseSchema(SubtaskSchema);

type SubtaskResponse = { data: Subtask };

/**
 * Subtasks Service
 * Handles subtask CRUD operations
 * API.md: Subtasks section
 */
export const subtasksService = {
  /**
   * Create a new subtask for a task
   * API.md: POST /api/v1/tasks/{task_id}/subtasks
   *
   * @param taskId - UUID of the parent task
   * @param data - Subtask creation request (title required, order_index optional)
   * @returns Created subtask wrapped in DataResponse
   * @throws ApiError with code VALIDATION_ERROR if invalid data (title 1-200 chars)
   * @throws ApiError with code NOT_FOUND if task doesn't exist
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await subtasksService.createSubtask(
   *   '550e8400-e29b-41d4-a716-446655440001',
   *   {
   *     title: 'Research similar proposals',
   *     order_index: 0
   *   }
   * );
   * const newSubtask = response.data;
   * ```
   */
  async createSubtask(taskId: string, data: CreateSubtaskRequest): Promise<SubtaskResponse> {
    // Validate request schema
    CreateSubtaskRequestSchema.parse(data);

    const response = await apiClient.post<SubtaskResponse>(
      `/tasks/${taskId}/subtasks`,
      data,
      SubtaskResponseSchema
    );

    return response;
  },

  /**
   * Update a subtask (toggle completion, change title, or reorder)
   * API.md: PATCH /api/v1/subtasks/{subtask_id}
   *
   * @param subtaskId - UUID of the subtask to update
   * @param data - Subtask update request (all fields optional)
   * @returns Updated subtask wrapped in DataResponse
   * @throws ApiError with code NOT_FOUND if subtask doesn't exist
   * @throws ApiError with code VALIDATION_ERROR if invalid data
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * // Toggle completion
   * const response = await subtasksService.updateSubtask(
   *   '550e8400-e29b-41d4-a716-446655440002',
   *   { completed: true }
   * );
   * const updatedSubtask = response.data;
   * ```
   */
  async updateSubtask(subtaskId: string, data: UpdateSubtaskRequest): Promise<SubtaskResponse> {
    // Validate request schema
    UpdateSubtaskRequestSchema.parse(data);

    const response = await apiClient.patch<SubtaskResponse>(
      `/subtasks/${subtaskId}`,
      data,
      SubtaskResponseSchema
    );

    return response;
  },

  /**
   * Delete a subtask permanently
   * API.md: DELETE /api/v1/subtasks/{subtask_id}
   *
   * @param subtaskId - UUID of the subtask to delete
   * @returns void (204 No Content)
   * @throws ApiError with code NOT_FOUND if subtask doesn't exist
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * await subtasksService.deleteSubtask('550e8400-e29b-41d4-a716-446655440002');
   * ```
   */
  async deleteSubtask(subtaskId: string): Promise<void> {
    await apiClient.delete<void>(`/subtasks/${subtaskId}`);
  },
};
