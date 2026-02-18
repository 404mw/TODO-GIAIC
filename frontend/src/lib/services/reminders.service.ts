import { apiClient } from '@/lib/api/client';
import { DataResponseSchema } from '@/lib/schemas/response.schema';
import {
  ReminderSchema,
  CreateReminderRequestSchema,
  type Reminder,
  type CreateReminderRequest,
} from '@/lib/schemas/reminder.schema';

// Response schemas for reminders (following DataResponse pattern)
const ReminderResponseSchema = DataResponseSchema(ReminderSchema);

type ReminderResponse = { data: Reminder };

/**
 * Reminders Service
 * Handles reminder CRUD operations for tasks
 * API.md: Reminders section
 */
export const remindersService = {
  /**
   * Create a new reminder for a task
   * API.md: POST /api/v1/tasks/{task_id}/reminders
   *
   * @param taskId - UUID of the parent task
   * @param data - Reminder creation request (type, scheduled_at, optional offset_minutes and method)
   * @returns Created reminder wrapped in DataResponse
   * @throws ApiError with code VALIDATION_ERROR if invalid data
   * @throws ApiError with code NOT_FOUND if task doesn't exist
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * const response = await remindersService.createReminder(
   *   '550e8400-e29b-41d4-a716-446655440001',
   *   {
   *     type: 'relative',
   *     offset_minutes: -15,  // 15 minutes before due date
   *     scheduled_at: '2026-02-15T16:45:00.000Z',
   *     method: 'in_app'
   *   }
   * );
   * const newReminder = response.data;
   * ```
   *
   * @note Reminder types: relative (offset from due date), absolute (specific time)
   * @note Notification methods: in_app, email, push
   * @note Use negative offset_minutes for "before" reminders (e.g., -15 = 15 min before)
   */
  async createReminder(taskId: string, data: CreateReminderRequest): Promise<ReminderResponse> {
    // Validate request schema
    CreateReminderRequestSchema.parse(data);

    const response = await apiClient.post<ReminderResponse>(
      `/tasks/${taskId}/reminders`,
      data,
      ReminderResponseSchema
    );

    return response;
  },

  /**
   * Delete a reminder permanently
   * API.md: DELETE /api/v1/reminders/{reminder_id}
   *
   * @param reminderId - UUID of the reminder to delete
   * @returns void (204 No Content)
   * @throws ApiError with code NOT_FOUND if reminder doesn't exist
   * @throws ApiError with code UNAUTHORIZED if not authenticated
   * @throws ApiError with code TOKEN_EXPIRED if access token expired
   *
   * @example
   * ```ts
   * await remindersService.deleteReminder('550e8400-e29b-41d4-a716-446655440002');
   * ```
   */
  async deleteReminder(reminderId: string): Promise<void> {
    await apiClient.delete<void>(`/reminders/${reminderId}`);
  },
};
