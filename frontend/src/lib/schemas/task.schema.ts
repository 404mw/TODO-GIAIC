import { z } from 'zod';
import { PrioritySchema, CompletedBySchema } from './common.schema';
import { SubtaskSchema } from './subtask.schema';
import { ReminderSchema } from './reminder.schema';
import { AchievementUnlockSchema } from './achievement.schema';
import { DataResponseSchema, PaginatedResponseSchema } from './response.schema';

/**
 * Task schema matching backend TaskInstance model.
 * Per API.md Tasks section (FR-014)
 */
export const TaskSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  template_id: z.string().uuid().nullable(),

  // Task details (API.md validation: title 1-500 chars, description max 5000 chars)
  title: z.string().min(1).max(500),
  description: z.string().max(5000).default(''),
  priority: PrioritySchema.default('medium'),
  due_date: z.string().datetime().nullable(),
  estimated_duration: z.number().int().min(1).max(720).nullable(),

  // Focus tracking
  focus_time_seconds: z.number().int().min(0).default(0),

  // Completion tracking
  completed: z.boolean().default(false),
  completed_at: z.string().datetime().nullable(),
  completed_by: CompletedBySchema.nullable(),

  // Status flags
  hidden: z.boolean().default(false),
  archived: z.boolean().default(false),

  // Subtask counts (added in list view per API.md)
  subtask_count: z.number().int().min(0).default(0),
  subtask_completed_count: z.number().int().min(0).default(0),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  version: z.number().int(),
});

/**
 * Task Detail schema matching backend TaskInstance with nested data
 * API.md: GET /api/v1/tasks/{task_id} returns task with subtasks[] and reminders[]
 */
export const TaskDetailSchema = TaskSchema.extend({
  subtasks: z.array(SubtaskSchema).default([]),
  reminders: z.array(ReminderSchema).default([]),
});

/**
 * Task Template schema matching backend TaskTemplate model.
 * Per data-model.md Entity 3 (FR-015)
 */
export const TaskTemplateSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Template details (using description instead of message)
  title: z.string().min(1).max(500),
  description: z.string().max(5000).default(''),
  priority: PrioritySchema.default('medium'),
  estimated_duration: z.number().int().min(1).max(720).nullable(),

  // Recurrence
  rrule: z.string(),
  next_due: z.string().datetime().nullable(),
  active: z.boolean().default(true),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Request schema for creating a task
 * API.md: POST /api/v1/tasks
 */
export const CreateTaskRequestSchema = TaskSchema.pick({
  title: true,
  description: true,
  priority: true,
  due_date: true,
  estimated_duration: true,
}).partial({
  description: true,
  priority: true,
  due_date: true,
  estimated_duration: true,
});

/**
 * Request schema for updating a task
 * API.md: PATCH /api/v1/tasks/{task_id}
 * Requires version field for optimistic locking
 */
export const UpdateTaskRequestSchema = TaskSchema.pick({
  title: true,
  description: true,
  priority: true,
  due_date: true,
  estimated_duration: true,
  archived: true,
  version: true,
})
  .partial()
  .required({ version: true });

/**
 * Request schema for force-completing a task
 * API.md: POST /api/v1/tasks/{task_id}/force-complete
 */
export const ForceCompleteTaskRequestSchema = z.object({
  version: z.number().int(),
});

/**
 * Task list response schema
 * API.md: GET /api/v1/tasks returns paginated list
 */
export const TaskListResponseSchema = PaginatedResponseSchema(TaskSchema);

/**
 * Task detail response schema
 * API.md: GET /api/v1/tasks/{task_id} returns task with subtasks and reminders
 */
export const TaskDetailResponseSchema = DataResponseSchema(TaskDetailSchema);

/**
 * Task create/update response schema
 * API.md: POST/PATCH /api/v1/tasks returns single task in data wrapper
 */
export const TaskResponseSchema = DataResponseSchema(TaskSchema);

/**
 * Task force-complete response schema
 * API.md: POST /api/v1/tasks/{task_id}/force-complete
 * Returns task, unlocked achievements, and streak
 */
export const TaskForceCompleteResponseSchema = DataResponseSchema(
  z.object({
    task: TaskSchema,
    unlocked_achievements: z.array(AchievementUnlockSchema),
    streak: z.number().int().min(0),
  })
);

/**
 * Task delete response schema
 * API.md: DELETE /api/v1/tasks/{task_id}
 * Returns tombstone_id and recoverable_until
 */
export const TaskDeleteResponseSchema = DataResponseSchema(
  z.object({
    tombstone_id: z.string().uuid(),
    recoverable_until: z.string().datetime(),
  })
);

// Type exports
export type Task = z.infer<typeof TaskSchema>;
export type TaskDetail = z.infer<typeof TaskDetailSchema>;
export type TaskTemplate = z.infer<typeof TaskTemplateSchema>;
export type CreateTaskRequest = z.infer<typeof CreateTaskRequestSchema>;
export type UpdateTaskRequest = z.infer<typeof UpdateTaskRequestSchema>;
export type ForceCompleteTaskRequest = z.infer<typeof ForceCompleteTaskRequestSchema>;
export type TaskListResponse = z.infer<typeof TaskListResponseSchema>;
export type TaskDetailResponse = z.infer<typeof TaskDetailResponseSchema>;
export type TaskResponse = z.infer<typeof TaskResponseSchema>;
export type TaskForceCompleteResponse = z.infer<typeof TaskForceCompleteResponseSchema>;
export type TaskDeleteResponse = z.infer<typeof TaskDeleteResponseSchema>;
